from django.shortcuts import render, redirect
from django.views import View

from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Balance, Category
from .forms import BalanceForm, YearForm

from django.db.models import Q

import datetime


class BalanceView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):

        categories = Category.objects.all()

        # 検索処理(TODO:この検索処理はオミットべきか？)
        if "search" in request.GET:

            if request.GET["search"] == "" or request.GET["search"].isspace():
                return redirect("asset:index")

            search = request.GET["search"].replace(" ", "　")
            search_list = search.split(" ")

            query = Q()
            for word in search_list:
                query &= Q(title__contains=word)

            balances = Balance.objects.filter(query)
        else:
            balances = Balance.objects.all()

        # 最古から最新の年リストを生成(決済日)
        dt = datetime.datetime.now()
        now_year = dt.year  # ←最新の決算日の年を当てるべきでは？
        years = []

        balance = Balance.objects.order_by("pay_dt").first()

        # 最古のデータがあれば最古のデータの年から今年までのリストを作る。(これがテンプレートのselectタグになる。)
        # なければ今年だけ表示
        if balance:
            old_year = balance.pay_dt.year
            print(old_year)
            for i in range(now_year, old_year - 1, -1):
                years.append(i)
        else:
            years.append(now_year)

        # yearの指定があれば、年のデータを抜き取り検索する。指定がなければ現在の年を指定
        form = YearForm(request.GET)
        selected_year = now_year

        if form.is_valid():
            data = form.cleaned_data
            selected_year = data["year"]

        # 1年分のデータ
        balances = Balance.objects.filter(pay_dt__year=selected_year).order_by("pay_dt")

        # 月ごとのデータ
        months = []
        for i in range(1, 13):
            months.append(Balance.objects.filter(pay_dt__year=selected_year, pay_dt__month=i).order_by("pay_dt"))

        # 小計値の計算(1年分)
        balances = list(balances.values())
        total = 0

        for balance in balances:

            total = total + int(balance["income"]) - int(balance["spending"])
            balance["total"] = total

            # カテゴリ名を設定
            if balance["category_id"]:
                category = Category.objects.filter(id=balance["category_id"]).first()
                balance["category"] = category.name

        # 小計値の計算(月ごと)←TODO:処理系が1年分と同じなので、関数化させるべきかと
        month_list = []
        for month in months:

            month = list(month.values())
            total = 0

            # 一ヶ月の中にある1レコード分ずつ処理
            for m in month:

                total = total + int(m["income"]) - int(m["spending"])
                m["total"] = total

                # カテゴリ名を設定
                if m["category_id"]:
                    category = Category.objects.filter(id=m["category_id"]).first()
                    m["category"] = category.name

            month_list.append(month)

        context = {"balances": balances,
                   "categories": categories,
                   "years": years,
                   "months": month_list,
                   "selected_year": selected_year,
                   }

        return render(request, "asset/index.html", context)

    def post(self, request, *args, **kwargs):

        form = BalanceForm(request.POST)

        if form.is_valid():
            print("バリデーションOK")
            form.save()
        else:
            print("バリデーションNG")

        return redirect("asset:index")


index = BalanceView.as_view()


class BalanceDeleteView(LoginRequiredMixin, View):

    def post(self, request, pk, *args, **kwargs):
        balance = Balance.objects.filter(id=pk).first()
        balance.delete()

        return redirect("asset:index")


delete = BalanceDeleteView.as_view()