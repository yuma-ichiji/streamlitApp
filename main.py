import streamlit as st
import requests
import pandas as pd
from datetime import datetime,timedelta
import streamlit.components.v1 as components
st.set_page_config(page_title="為替レート変換アプリ",page_icon="💱",layout="wide")
st.title("為替レート変換アプリ")
currency_names={
    "AED":"UAEディルハム - UAE Dirham",
    "AUD":"豪ドル - Australian Dollar",
    "BGN":"ブルガリア・レフ - Bulgarian Lev",
    "BRL":"ブラジル・レアル - Brazilian Real",
    "CAD":"カナダドル - Canadian Dollar",
    "CHF":"スイスフラン - Swiss Franc",
    "CNY":"中国人民元 - Chinese Yuan",
    "CZK":"チェコ・コルナ - Czech Koruna",
    "DKK":"デンマーク・クローネ - Danish Krone",
    "EUR":"ユーロ - Euro",
    "GBP":"イギリスポンド - British Pound",
    "HKD":"香港ドル - Hong Kong Dollar",
    "HUF":"ハンガリー・フォリント - Hungarian Forint",
    "IDR":"インドネシア・ルピア - Indonesian Rupiah",
    "ILS":"イスラエル・シェケル - Israeli New Shekel",
    "INR":"インド・ルピー - Indian Rupee",
    "ISK":"アイスランド・クローナ - Icelandic Króna",
    "JPY":"日本円 - Japanese Yen",
    "KRW":"韓国ウォン - South Korean Won",
    "MXN":"メキシコ・ペソ - Mexican Peso",
    "MYR":"マレーシア・リンギット - Malaysian Ringgit",
    "NOK":"ノルウェー・クローネ - Norwegian Krone",
    "NZD":"ニュージーランドドル - New Zealand Dollar",
    "PHP":"フィリピン・ペソ - Philippine Peso",
    "PLN":"ポーランド・ズウォティ - Polish Złoty",
    "RON":"ルーマニア・レウ - Romanian Leu",
    "SEK":"スウェーデン・クローナ - Swedish Krona",
    "SGD":"シンガポールドル - Singapore Dollar",
    "THB":"タイ・バーツ - Thai Baht",
    "TRY":"トルコ・リラ - Turkish Lira",
    "USD":"米ドル - US Dollar",
    "ZAR":"南アフリカ・ランド - South African Rand",
    "BHD":"バーレーン・ディナール - Bahraini Dinar",
    "CLP":"チリ・ペソ - Chilean Peso",
    "COP":"コロンビア・ペソ - Colombian Peso",
    "CRC":"コスタリカ・コロン - Costa Rican Colón",
    "EGP":"エジプト・ポンド - Egyptian Pound",
    "GEL":"ジョージア・ラリ - Georgian Lari",
    "GTQ":"グアテマラ・ケツァル - Guatemalan Quetzal",
    "ISK":"アイスランド・クローナ - Icelandic Króna",
    "JOD":"ヨルダン・ディナール - Jordanian Dinar",
    "KES":"ケニア・シリング - Kenyan Shilling",
    "KWD":"クウェート・ディナール - Kuwaiti Dinar",
    "MAD":"モロッコ・ディルハム - Moroccan Dirham",
    "MDL":"モルドバ・レウ - Moldovan Leu",
    "MUR":"モーリシャス・ルピー - Mauritian Rupee",
    "NAD":"ナミビア・ドル - Namibian Dollar",
    "NGN":"ナイジェリア・ナイラ - Nigerian Naira",
    "OMR":"オマーン・リアル - Omani Rial",
    "PEN":"ペルー・ソル - Peruvian Sol",
    "PKR":"パキスタン・ルピー - Pakistani Rupee",
    "QAR":"カタール・リヤル - Qatari Riyal",
    "RSD":"セルビア・ディナール - Serbian Dinar",
    "SAR":"サウジアラビア・リヤル - Saudi Riyal",
    "THB":"タイ・バーツ - Thai Baht",
    "TND":"チュニジア・ディナール - Tunisian Dinar",
    "UGX":"ウガンダ・シリング - Ugandan Shilling",
    "UYU":"ウルグアイ・ペソ - Uruguayan Peso",
    "VES":"ベネズエラ・ボリバル - Venezuelan Bolívar",
    "XOF":"CFAフラン - West African CFA Franc",
    "ZMW":"ザンビア・クワチャ - Zambian Kwacha"
}
@st.cache_data(ttl=3600)
def get_currencies():
    try:
        response=requests.get("https://api.frankfurter.app/currencies",timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception:
        return {"JPY":"Japanese Yen","USD":"US Dollar"}
currency_data=get_currencies()
preferred_codes=["JPY","USD"]
currencies={}
for code in preferred_codes:
    if code in currency_data:
        japanese_name=currency_names.get(code,currency_data[code])
        currencies[f"{japanese_name} ({code})"]=code
for code,name in currency_data.items():
    if code not in preferred_codes:
        japanese_name=currency_names.get(code,name)
        currencies[f"{japanese_name} ({code})"]=code
currency_list=list(currencies.keys())
if "from_currency" not in st.session_state:
    st.session_state.from_currency=currency_list[0]
if "to_currency" not in st.session_state:
    st.session_state.to_currency=currency_list[min(1,len(currency_list)-1)]
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh=False
if "alert_enabled" not in st.session_state:
    st.session_state.alert_enabled=False
if "alert_was_triggered" not in st.session_state:
    st.session_state.alert_was_triggered=False
components.html("""
<div id="clock" style="font-size:24px;font-weight:bold;text-align:center;"></div>
<script>
function updateClock(){
    const now=new Date();
    const y=now.getFullYear();
    const m=String(now.getMonth()+1).padStart(2,"0");
    const d=String(now.getDate()).padStart(2,"0");
    const h=String(now.getHours()).padStart(2,"0");
    const min=String(now.getMinutes()).padStart(2,"0");
    const s=String(now.getSeconds()).padStart(2,"0");
    document.getElementById("clock").textContent=y+"年"+m+"月"+d+"日 "+h+":"+min+":"+s;
}
updateClock();
setInterval(updateClock,1000);
</script>
""",height=50)
tab1,tab2,tab3=st.tabs(["為替レート変換とグラフ","電卓","このアプリについて"])
with tab1:
    st.subheader("為替レート変換")
    col1,col2=st.columns([5,1])
    with col1:
        amount=st.number_input("金額",min_value=0.0,value=1000.0,step=100.0)
    with col2:
        st.write("")
        st.write("")
        if st.button("通貨を入れ替える",use_container_width=True):
            st.session_state.from_currency,st.session_state.to_currency=st.session_state.to_currency,st.session_state.from_currency
            st.rerun()
    col1,col2=st.columns(2)
    with col1:
        from_currency=st.selectbox(
            "変換元の通貨",
            currency_list,
            index=currency_list.index(st.session_state.from_currency),
            key="from_currency"
        )
    with col2:
        to_currency=st.selectbox(
            "変換先の通貨",
            currency_list,
            index=currency_list.index(st.session_state.to_currency),
            key="to_currency"
        )
    from_code=currencies[from_currency]
    to_code=currencies[to_currency]
    if st.button("変換する",use_container_width=True):
        try:
            url=f"https://api.frankfurter.app/latest?amount={amount}&from={from_code}&to={to_code}"
            response=requests.get(url,timeout=10)
            response.raise_for_status()
            data=response.json()
            result=data["rates"][to_code]
            now=datetime.now()
            st.success(f"{amount:,.2f} {from_code} = {result:,.6f} {to_code}")
            st.info(f"変換日時: {now.strftime('%Y年%m月%d日 %H:%M:%S')}")
        except Exception as e:
            st.error(f"為替レートの取得に失敗しました: {e}")
    st.divider()
    st.subheader("更新設定")
    auto_refresh=st.checkbox("自動更新する",key="auto_refresh")
    refresh_seconds=st.selectbox(
        "更新間隔",
        [10,30,60,120,300,600],
        index=0,
        format_func=lambda x:f"{x}秒"
    )
    if st.button("更新",use_container_width=True):
        st.rerun()
    run_every=f"{refresh_seconds}s" if st.session_state.auto_refresh else None
    @st.fragment(run_every=run_every)
    def show_exchange_data():
        st.subheader("為替レートのグラフ")
        period=st.selectbox("グラフ期間",["7日","30日","90日","365日"],key="graph_period")
        days={"7日":7,"30日":30,"90日":90,"365日":365}[period]
        end_date=datetime.now().date()
        start_date=end_date-timedelta(days=days)
        try:
            url=f"https://api.frankfurter.app/{start_date.isoformat()}..{end_date.isoformat()}?from={from_code}&to={to_code}"
            response=requests.get(url,timeout=10)
            response.raise_for_status()
            data=response.json()
            rates=data.get("rates",{})
            if not rates:
                st.warning("グラフ用のデータがありません。")
                return
            chart_data=[]
            for date,rates_for_date in rates.items():
                if to_code in rates_for_date:
                    chart_data.append({
                        "日付":date,
                        "レート":float(rates_for_date[to_code])
                    })
            chart_data=pd.DataFrame(chart_data)
            if chart_data.empty:
                st.warning("グラフ用のデータがありません。")
                return
            chart_data["日付"]=pd.to_datetime(chart_data["日付"])
            chart_data=chart_data.sort_values("日付")
            latest_rate=float(chart_data["レート"].iloc[-1])
            highest_rate=float(chart_data["レート"].max())
            lowest_rate=float(chart_data["レート"].min())
            average_rate=float(chart_data["レート"].mean())
            first_rate=float(chart_data["レート"].iloc[0])
            rate_change=latest_rate-first_rate
            if first_rate!=0:
                rate_change_percent=(rate_change/first_rate)*100
            else:
                rate_change_percent=0.0
            col1,col2,col3,col4,col5=st.columns(5)
            with col1:
                st.metric("最新レート",f"{latest_rate:.6f}")
            with col2:
                st.metric("最高値",f"{highest_rate:.6f}")
            with col3:
                st.metric("最低値",f"{lowest_rate:.6f}")
            with col4:
                st.metric("平均値",f"{average_rate:.6f}")
            with col5:
                st.metric("レートの変化",f"{rate_change_percent:+.2f}%",delta=f"{rate_change:+.6f}")
            st.line_chart(
                chart_data.set_index("日付")["レート"],
                use_container_width=True
            )
            st.subheader("レートの変化")
            change_col1,change_col2,change_col3=st.columns(3)
            with change_col1:
                st.metric("期間開始時",f"{first_rate:.6f}")
            with change_col2:
                st.metric("現在",f"{latest_rate:.6f}")
            with change_col3:
                if rate_change_percent>0:
                    st.success(f"レート上昇: +{rate_change_percent:.2f}%")
                elif rate_change_percent<0:
                    st.error(f"レート下降: {rate_change_percent:.2f}%")
                else:
                    st.info("レート変化なし: 0.00%")
            st.subheader("過去の為替レート")
            display_data=chart_data.copy()
            display_data["日付"]=display_data["日付"].dt.strftime("%Y年%m月%d日")
            st.dataframe(display_data,use_container_width=True,hide_index=True)
            st.divider()
            st.subheader("レートアラート")
            if "alert_enabled" not in st.session_state:
                st.session_state.alert_enabled=False
            alert_enabled=st.toggle(
                "レートアラートを無効にする" if st.session_state.alert_enabled else "レートアラートを有効にする",
                key="alert_enabled"
)
            if alert_enabled:
                alert_rate=st.number_input(
                    "目標レート",
                    min_value=0.000001,
                    value=150.0,
                    step=0.1,
                    key="alert_rate"
                )
                alert_condition=st.selectbox(
                    "アラート条件",
                    ["以上になったら","以下になったら"],
                    key="alert_condition"
                )
                alert_triggered=False
                if alert_condition=="以上になったら" and latest_rate>=alert_rate:
                    alert_triggered=True
                elif alert_condition=="以下になったら" and latest_rate<=alert_rate:
                    alert_triggered=True
                if alert_triggered:
                    st.success(f"目標レートを達成しました。現在のレート: {latest_rate:.6f} {to_code}")
                    if not st.session_state.alert_was_triggered:
                        components.html("""
<script>
const audioContext=new(window.AudioContext||window.webkitAudioContext)();
const oscillator=audioContext.createOscillator();
const gainNode=audioContext.createGain();
oscillator.type="sine";
oscillator.frequency.setValueAtTime(880,audioContext.currentTime);
gainNode.gain.setValueAtTime(0.3,audioContext.currentTime);
oscillator.connect(gainNode);
gainNode.connect(audioContext.destination);
oscillator.start();
oscillator.stop(audioContext.currentTime+0.7);
</script>
""",height=0)
                    st.session_state.alert_was_triggered=True
                else:
                    st.session_state.alert_was_triggered=False
                    st.info(f"目標レート未達成。現在のレート: {latest_rate:.6f} {to_code}")
            else:
                st.session_state.alert_was_triggered=False
                st.info("レートアラートは現在オフです。")
        except Exception as e:
            st.error(f"グラフデータの取得に失敗しました: {e}")
    show_exchange_data()
with tab2:
    st.subheader("電卓")
    calc_col1,calc_col2=st.columns(2)
    with calc_col1:
        calc_a=st.number_input("計算する数値1",value=0.0,key="calc_a")
    with calc_col2:
        calc_b=st.number_input("計算する数値2",value=0.0,key="calc_b")
    operation=st.selectbox("計算方法",["足し算(+)","引き算(-)","掛け算(×)","割り算(÷)"],key="calc_operation")
    if st.button("計算する",use_container_width=True):
        if operation=="足し算(+)":
            calc_result=calc_a+calc_b
            st.success(f"計算結果: {calc_result:,.2f}")
        elif operation=="引き算(-)":
            calc_result=calc_a-calc_b
            st.success(f"計算結果: {calc_result:,.2f}")
        elif operation=="掛け算(×)":
            calc_result=calc_a*calc_b
            st.success(f"計算結果: {calc_result:,.2f}")
        elif operation=="割り算(÷)":
            if calc_b==0:
                st.error("0で割ることはできません。")
            else:
                calc_result=calc_a/calc_b
                st.success(f"計算結果: {calc_result:,.2f}")
with tab3:
    st.subheader("このアプリについて")
    st.write("このアプリはFrankfurter APIを利用して為替レートを取得しています。")
    st.caption("為替レートは変動するため、実際の銀行や両替所のレートとは異なる場合があります。")
    st.caption("このアプリは投資や取引の判断に使用しないでください。")
st.markdown(':color[このアプリを利用した詐欺に注意してください]{foreground="#ff0000"}')