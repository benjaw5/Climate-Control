from flask import Flask, request
import base64
from io import BytesIO
from matplotlib.figure import Figure
from datetime import datetime
import matplotlib.dates as mdates

app = Flask(__name__)
temp = []
humid = []
AQI = []
TVOC = []
CO2 = []
time = []

def co2_health():
    co2 = int(CO2[-1])
    if 600 > co2 >= 400:
        return "Healthy", "Your CO2 levels are excellent"
    elif 800 > co2 >= 600:
        return "Good", "Your CO2 levels are normal"
    elif 1000 > co2 >= 800:
        return "Fair", "You might want to ventilate your room"
    elif 1500 > co2 >= 1000:
        return "Poor", "Your room is poisonous"
    elif co2 >= 1500:
        return "Bad", "Evacuate"

def aqi_health():
    aqi = int(AQI[-1])
    if aqi == 1:
        return "Excellent", "Your air quality is healthy"
    elif aqi == 2:
        return "Good", "Your air quality is normal"
    elif aqi == "3":
        return "Moderate", "Risk of health issues if prolonged exposure for 12 months"
    elif aqi == 4:
        return "Poor", "Risk of health issues if prolonged exposure for 1 month"
    elif aqi == 5:
        return "Unhealthy", "Risk of health issues if prolonged exposure for hours"

def temp_humid_health():
    tmp = float(temp[-1])
    hum = float(humid[-1])

    if tmp >= 90 and hum >= 70:
        return "Unhealthy", "Your room is too hot and humid which can lead to heatstrokes or heat exhaustion"
    elif tmp <= 60 and hum <= 20:
        return "Unhealthy", "Your room too cold and dry which can lead to dehydration and respiratory irritation"
    else:
        return "Healthy", "Your room is at a comfortable temperature and humidity"

@app.route("/")
def hello():
    plots = []
    if len(temp) > 0 and len(humid) > 0 and len(AQI) > 0 and len(TVOC) > 0 and len(CO2) > 0:
        fig_temp = Figure()
        ax_temp = fig_temp.subplots()
        ax_temp.plot(time, temp, label="Temperature")
        ax_temp.set_title("Temperature Over Time")
        ax_temp.set_xlabel("Time")
        ax_temp.set_ylabel("Temperature")
        ax_temp.legend()
        ax_temp.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax_temp.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M:%S"))
        fig_temp.autofmt_xdate(rotation=45)
        fig_temp.tight_layout()
        buf_temp = BytesIO()
        fig_temp.savefig(buf_temp, format="png")
        data_temp = base64.b64encode(buf_temp.getbuffer()).decode("ascii")
        plots.append(f"<img src='data:image/png;base64,{data_temp}'/>")
        
        fig_humid = Figure()
        ax_humid = fig_humid.subplots()
        ax_humid.plot(time, humid, label='Humidity')
        ax_humid.set_title("Humidity Over Time")
        ax_humid.set_xlabel("Time")
        ax_humid.set_ylabel("Humidity")
        ax_humid.legend()
        ax_humid.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax_humid.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M:%S"))
        fig_humid.autofmt_xdate(rotation=45)
        fig_humid.tight_layout()
        buf_humid = BytesIO()
        fig_humid.savefig(buf_humid, format="png")
        data_humid = base64.b64encode(buf_humid.getbuffer()).decode("ascii")
        plots.append(f"<img src='data:image/png;base64,{data_humid}'/>")

        fig_aqi = Figure()
        ax_aqi = fig_aqi.subplots()
        ax_aqi.plot(time, AQI, label='AQI')
        ax_aqi.set_title("AQI Over Time")
        ax_aqi.set_xlabel("Time")
        ax_aqi.set_ylabel("AQI")
        ax_aqi.legend()
        ax_aqi.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax_aqi.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M:%S"))
        fig_aqi.autofmt_xdate(rotation=45)
        fig_aqi.tight_layout()
        buf_aqi = BytesIO()
        fig_aqi.savefig(buf_aqi, format="png")
        data_aqi = base64.b64encode(buf_aqi.getbuffer()).decode("ascii")
        plots.append(f"<img src='data:image/png;base64,{data_aqi}'/>")

        fig_tvoc = Figure()
        ax_tvoc = fig_tvoc.subplots()
        ax_tvoc.plot(time, TVOC, label='TVOC')
        ax_tvoc.set_title("TVOC Over Time")
        ax_tvoc.set_xlabel("Time")
        ax_tvoc.set_ylabel("TVOC")
        ax_tvoc.legend()
        ax_tvoc.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax_tvoc.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M:%S"))
        fig_tvoc.autofmt_xdate(rotation=45)
        fig_tvoc.tight_layout()
        buf_tvoc = BytesIO()
        fig_tvoc.savefig(buf_tvoc, format="png")
        data_tvoc = base64.b64encode(buf_tvoc.getbuffer()).decode("ascii")
        plots.append(f"<img src='data:image/png;base64,{data_tvoc}'/>")

        fig_co2 = Figure()
        ax_co2 = fig_co2.subplots()
        ax_co2.plot(time, CO2, label='CO2')
        ax_co2.set_title("CO2 Over Time")
        ax_co2.set_xlabel("Time")
        ax_co2.set_ylabel("CO2")
        ax_co2.legend()
        ax_co2.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax_co2.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M:%S"))
        fig_co2.autofmt_xdate(rotation=45)
        fig_co2.tight_layout()
        buf_co2 = BytesIO()
        fig_co2.savefig(buf_co2, format="png")
        data_co2 = base64.b64encode(buf_co2.getbuffer()).decode("ascii")
        plots.append(f"<img src='data:image/png;base64,{data_co2}'/>")
        
        co2_rating, co2_comment = co2_health()
        aqi_rating, aqi_comment = aqi_health()
        temp_humid_rating, temp_humid_comment = temp_humid_health()
        latest_values = f"""
        <h2>Anaylsis:</h2>
        <p>AQI Health Status: {aqi_rating}</p>
        <p>AQI Recommendation: {aqi_comment}</p>
        <p>CO2 Health Status: {co2_rating}</p>
        <p>CO2 Recommendation: {co2_comment}</p>
        <p>Temperature and Humid Health Status: {temp_humid_rating}</p>
        <p>Temperature and Humid Recommendation: {temp_humid_comment}</p>
        <h2>Data Analytics:</h2>
        <p><b>Latest Temperature:</b> {temp[-1]}</p>
        <p><b>Latest Humidity:</b> {humid[-1]}</p>
        <p><b>Latest AQI:</b> {AQI[-1]}</p>
        <p><b>Latest TVOC:</b> {TVOC[-1]}</p>
        <p><b>Latest CO2:</b> {CO2[-1]}</p>
        """

        return latest_values + "".join(plots)
    else:
        return "Retrieving Data..."

@app.route("/data/")
def data():
    temp.append(request.args.get("temp"))
    humid.append(request.args.get("humid"))
    AQI.append(request.args.get("aqi"))
    TVOC.append(request.args.get("tvoc"))
    CO2.append(request.args.get("co2"))
    time.append(datetime.now())
    return "data"
