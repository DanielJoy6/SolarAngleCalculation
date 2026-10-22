import math
from datetime import date, datetime, time, timedelta

import numpy as np

import streamlit as st

st.title("Johnny's Architecture Program")
st.subheader("A simple calculator for outputting overheat HSA & VSA")

st.write("Input your values below:")

col1, col2, col3 = st.columns(3)
with col1:
    st.write("Location")
    Latitude = st.number_input(
        label="Latitude",
        min_value=0,
        max_value=500,
        value=0,
    )
    Longitude = st.number_input(
        label="Longitude",
        min_value=0,
        max_value=500,
        value=0,
    )
    st.write("UTC = 0, EST = -5")
    Timezone = st.number_input(
        label="Timezone",
        min_value=-12,
        max_value=12,
        value=0,
    )
with col2:
    st.write("Specific Day:")
    Year = st.number_input(
        label="Year",
        min_value=0,
        max_value=2030,
        value=2026,
    )
    StartMonth = st.number_input(
        label="StartMonth",
        min_value=1,
        max_value=12,
        value=1,
    )
    EndMonth = st.number_input(
        label="EndMonth",
        min_value=1,
        max_value=12,
        value=1,
    )
    StartDay = st.number_input(
        label="StartDay",
        min_value=1,
        max_value=31,
        value=1,
    )
    EndDay = st.number_input(
        label="EndDay",
        min_value=1,
        max_value=31,
        value=10,
    )
with col3:
    st.write("Overheat Range:")
    StartHour = st.number_input(
        label="Start Hour",
        min_value=1,
        max_value=12,
        value=6,
    )
    EndHour = st.number_input(
        label="End Hour",
        min_value=1,
        max_value=12,
        value=7,
    )
    StartMinute = st.number_input(
        label="Start Minute",
        min_value=0,
        max_value=59,
        value=0,
    )
    EndMinute = st.number_input(
        label="End Minute",
        min_value=0,
        max_value=59,
        value=0,
    )
    HSAOverHeatPeriod = st.selectbox(
        label="Choose an HSA analysis type:",
        options=["max", "median", "min"]
    )
    VSAOverHeatPeriod = st.selectbox(
        label="Choose a VSA analysis type:",
        options=["max", "median", "min"]
    )

# Overheat period day & times

AngleFinfromSouth = 0
AngleFacadefromSouth = 0

# Calculations
def CalculateSolarPosition(Year, Month, Day, Hour, Minute, Latitude, Longitude, Timezone):
    dt = datetime(Year, Month, Day, Hour, Minute)
    Date = (dt.date() - date(1899, 12, 30)).days
    Time = (Hour + Minute / 60) / 24
    JulianDay = Date + 2415018.5 + Time - Timezone / 24
    JulianCentury = (JulianDay - 2451545) / 36525
    
    # Solar Geometry
    GeomMeanLongSun = (280.46646 + JulianCentury * (36000.76983 + JulianCentury * 0.0003032)) % 360
    GeomMeanAnomSun = 357.52911 + JulianCentury * (35999.05029 - 0.0001537 * JulianCentury)
    EccentEarthOrbit = 0.016708634 - JulianCentury * (0.000042037 + 0.0000001267 * JulianCentury)
    SunEqofCtr = math.sin(math.radians(GeomMeanAnomSun)) * (1.914602 - JulianCentury * (0.004817 + 0.000014 * JulianCentury)) + math.sin(math.radians(2 * GeomMeanAnomSun)) * (0.019993 - 0.000101 * JulianCentury) + math.sin(math.radians(3 * GeomMeanAnomSun)) * 0.000289
    SunTrueLong = GeomMeanLongSun + SunEqofCtr
    SunTrueAnom = GeomMeanAnomSun + SunEqofCtr
    SunRadVector = (1.000001018 * (1 - EccentEarthOrbit**2)) / (1 + EccentEarthOrbit * math.cos(math.radians(SunTrueAnom)))
    SunAppLong = SunTrueLong - 0.00569 - 0.00478 * math.sin(math.radians(125.04 - 1934.136 * JulianCentury))
    MeanObliqEcliptic = 23 + (26 + (21.448 - JulianCentury * (46.815 + JulianCentury * (0.00059 - JulianCentury * 0.001813))) / 60) / 60
    ObliqCorr = MeanObliqEcliptic + 0.00256 * math.cos(math.radians(125.04 - 1934.136 * JulianCentury))
    SunRtAscen = math.degrees(math.atan2(math.cos(math.radians(ObliqCorr)) * math.sin(math.radians(SunAppLong)), math.cos(math.radians(SunAppLong))))
    SunDeclin = math.degrees(math.asin(math.sin(math.radians(ObliqCorr)) * math.sin(math.radians(SunAppLong))))
    vary = math.tan(math.radians(ObliqCorr / 2))**2
    
    # Equation of Time
    EqofTime = 4 * math.degrees(vary * math.sin(2 * math.radians(GeomMeanLongSun)) - 2 * EccentEarthOrbit * math.sin(math.radians(GeomMeanAnomSun)) + 4 * EccentEarthOrbit * vary * math.sin(math.radians(GeomMeanAnomSun)) * math.cos(2 * math.radians(GeomMeanLongSun)) - 0.5 * vary**2 * math.sin(4 * math.radians(GeomMeanLongSun)) - 1.25 * EccentEarthOrbit**2 * math.sin(2 * math.radians(GeomMeanAnomSun))) # minutes
    
    # Sunrise / Sunset
    sunrise_argument = math.cos(math.radians(90.833)) / (math.cos(math.radians(Latitude)) * math.cos(math.radians(SunDeclin))) - math.tan(math.radians(Latitude)) * math.tan(math.radians(SunDeclin))
    HASunrise = math.degrees(math.acos(sunrise_argument)) if -1 <= sunrise_argument <= 1 else None
    SolarNoon = (720 - 4 * Longitude - EqofTime + Timezone * 60) / 1440
    SunriseTime = SolarNoon - HASunrise * 4 / 1440 if HASunrise is not None else None
    SunsetTime = SolarNoon + HASunrise * 4 / 1440 if HASunrise is not None else None
    SunlightDuration = 8 * HASunrise if HASunrise is not None else None
    
    # Solar Time / Hour Angle
    TrueSolarTime = (Time * 1440 + EqofTime + 4 * Longitude - 60 * Timezone) % 1440
    HourAngle = TrueSolarTime / 4 - 180
    
    # Solar Zenith / Altitude
    zenith_argument = math.sin(math.radians(Latitude)) * math.sin(math.radians(SunDeclin)) + math.cos(math.radians(Latitude)) * math.cos(math.radians(SunDeclin)) * math.cos(math.radians(HourAngle))
    SolarZenithAngle = math.degrees(math.acos(max(-1.0, min(1.0, zenith_argument))))
    SolarAltitudeAngle = 90 - SolarZenithAngle
    
    # Atmospheric Refraction
    if SolarAltitudeAngle > 85:
        AppAtmosphericRefraction = 0
    elif SolarAltitudeAngle > 5:
        AppAtmosphericRefraction = (58.1 / math.tan(math.radians(SolarAltitudeAngle)) - 0.07 / math.tan(math.radians(SolarAltitudeAngle))**3 + 0.000086 / math.tan(math.radians(SolarAltitudeAngle))**5) / 3600
    elif SolarAltitudeAngle > -0.575:
        AppAtmosphericRefraction = (1735 + SolarAltitudeAngle * (-518.2 + SolarAltitudeAngle * (103.4 + SolarAltitudeAngle * (-12.79 + SolarAltitudeAngle * 0.711)))) / 3600
    else:
        AppAtmosphericRefraction = (-20.772 / math.tan(math.radians(SolarAltitudeAngle))) / 3600
    
    SolarElevationcorrected = SolarAltitudeAngle + AppAtmosphericRefraction
    
    # Solar Azimuth
    
    azimuth_argument = (math.sin(math.radians(Latitude)) * math.cos(math.radians(SolarZenithAngle)) - math.sin(math.radians(SunDeclin))) / (math.cos(math.radians(Latitude)) * math.sin(math.radians(SolarZenithAngle)))
    azimuth = math.acos(azimuth_argument)

    if HourAngle > 0:
        SolarAzimuthAngle = (math.degrees(azimuth) + 180) % 360
    else:
        SolarAzimuthAngle = (540 - math.degrees(azimuth)) % 360


    results = {
        "Date": Date,
        "Time": Time,
        "JulianDay": JulianDay,
        "JulianCentury": JulianCentury,
        "GeomMeanLongSun": GeomMeanLongSun,
        "GeomMeanAnomSun": GeomMeanAnomSun,
        "EccentEarthOrbit": EccentEarthOrbit,
        "SunEqofCtr": SunEqofCtr,
        "SunTrueLong": SunTrueLong,
        "SunTrueAnom": SunTrueAnom,
        "SunRadVector": SunRadVector,
        "SunAppLong": SunAppLong,
        "MeanObliqEcliptic": MeanObliqEcliptic,
        "ObliqCorr": ObliqCorr,
        "SunRtAscen": SunRtAscen,
        "SunDeclin": SunDeclin,
        "vary": vary,
        "EqofTime": EqofTime,
        "HASunrise": HASunrise,
        "SolarNoon": SolarNoon,
        "SunriseTime": SunriseTime,
        "SunsetTime": SunsetTime,
        "SunlightDuration": SunlightDuration,
        "TrueSolarTime": TrueSolarTime,
        "HourAngle": HourAngle,
        "SolarZenithAngle": SolarZenithAngle,
        "SolarAltitudeAngle": SolarAltitudeAngle,
        "AppAtmosphericRefraction": AppAtmosphericRefraction,
        "SolarElevationcorrected": SolarElevationcorrected,
        "SolarAzimuthAngle": SolarAzimuthAngle,
    }
    return results

# Building Facade Calculations
def CalculateOverheating(solar, previous_altitude, minimum_altitude, maximum_altitude, Calculation_E16, Calculation_E17, Calculation_E18, Calculation_E19, ReformattedWallAngle, FinAzimuth):
    SolarAltitudeAngle = solar["SolarAltitudeAngle"]
    SolarAzimuthAngle = solar["SolarAzimuthAngle"]
    Date, Time = solar["Date"], solar["Time"]
    OverheatPeriodAnalysis = (Calculation_E16 <= Time <= Calculation_E17 and Calculation_E18 <= Date <= Calculation_E19 and SolarAltitudeAngle >= 0 and (SolarAltitudeAngle > previous_altitude or math.isclose(SolarAltitudeAngle, minimum_altitude, abs_tol=1e-9) or math.isclose(SolarAltitudeAngle, maximum_altitude, abs_tol=1e-9)) and abs((SolarAzimuthAngle - ReformattedWallAngle + 180) % 360 - 180) <= 90) if SolarAzimuthAngle is not None else False
    HSAofBuildingFacade = (SolarAzimuthAngle - ReformattedWallAngle + 180) % 360 - 180 if OverheatPeriodAnalysis else None
    FinHSA = (SolarAzimuthAngle - FinAzimuth + 540) % 360 - 180 if OverheatPeriodAnalysis else None
    hsa_cos = math.cos(math.radians(HSAofBuildingFacade)) if OverheatPeriodAnalysis else None
    fin_cos = math.cos(math.radians(FinHSA)) if OverheatPeriodAnalysis else None
    VSAofBuildingFacade = math.degrees(math.atan(math.tan(math.radians(SolarAltitudeAngle)) / hsa_cos)) if OverheatPeriodAnalysis and abs(hsa_cos) > 1e-12 else None
    FinVSA = math.degrees(math.atan(math.tan(math.radians(SolarAltitudeAngle)) / fin_cos)) if OverheatPeriodAnalysis and abs(fin_cos) > 1e-12 else None
    results = {
        "OverheatPeriodAnalysis": OverheatPeriodAnalysis,
        "HSAofBuildingFacade": HSAofBuildingFacade,
        "VSAofBuildingFacade": VSAofBuildingFacade,
        "FinHSA": FinHSA,
        "FinVSA": FinVSA
    }
    return results


def calculate():
    # Converted to Excel-compatible values
    Calculation_E16 = (StartTime.hour + StartTime.minute / 60) / 24
    Calculation_E17 = (EndTime.hour + EndTime.minute / 60) / 24
    Calculation_E18 = (date(Year, StartMonth, StartDay) - date(1899, 12, 30)).days
    Calculation_E19 = (date(Year, EndMonth, EndDay) - date(1899, 12, 30)).days

    # Building Orientation
    ReformattedWallAngle = (180 - AngleFacadefromSouth) % 360
    ReformattedFinAngle = (180 - AngleFinfromSouth) % 360
    FinAzimuth = (ReformattedWallAngle + ReformattedFinAngle) % 360

    # Calculate all 30-minute solar positions once.
    positions = {}
    altitudes = {}
    current = datetime(Year, 1, 1)
    end = datetime(Year + 1, 1, 1)

    while current < end:
        solar_result = CalculateSolarPosition(current.year, current.month, current.day, current.hour, current.minute, Latitude, Longitude, Timezone)
        positions[current] = solar_result
        altitudes[current] = solar_result["SolarAltitudeAngle"]
        current += timedelta(minutes=30)

    MinimumAltitude = min(altitudes.values())
    MaximumAltitude = max(altitudes.values())

    '''
    # Calculate overheat for the selected date/time.
    dt = datetime(Year, Month, Day, Hour, Minute)
    solar = CalculateSolarPosition(Year, Month, Day, Hour, Minute, Latitude, Longitude, Timezone)

    previous_dt = dt - timedelta(minutes=30)
    previous_solar = CalculateSolarPosition(previous_dt.year, previous_dt.month, previous_dt.day, previous_dt.hour, previous_dt.minute, Latitude, Longitude, Timezone)
    previous_altitude = previous_solar["SolarAltitudeAngle"]

    overheat = CalculateOverheating(solar, previous_altitude, MinimumAltitude, MaximumAltitude, Calculation_E16, Calculation_E17, Calculation_E18, Calculation_E19, ReformattedWallAngle, FinAzimuth)
    '''

    # Calculate statistics for the relevant date/time window.
    start_date = date(Year, StartMonth, StartDay)
    end_date = date(Year, EndMonth, EndDay)
    relevant_altitudes = {}
    HSAs, fHSAs, VSAs, fVSAs = [], [], [], []
    current = datetime(Year, 1, 1)

    #Calculate HSA, VSA, fins for included range
    while current < end:
        if start_date <= current.date() <= end_date and StartTime <= current.time() <= EndTime:
            previous_dt = current - timedelta(minutes=30)

            previous_solar = CalculateSolarPosition(previous_dt.year, previous_dt.month, previous_dt.day, previous_dt.hour, previous_dt.minute, Latitude, Longitude, Timezone)
            previous_altitude = previous_solar["SolarAltitudeAngle"]
            analysis = CalculateOverheating(positions[current], previous_altitude, MinimumAltitude, MaximumAltitude, Calculation_E16, Calculation_E17, Calculation_E18, Calculation_E19, ReformattedWallAngle, FinAzimuth)
            if analysis["OverheatPeriodAnalysis"]:
                relevant_altitudes[current] = altitudes[current]
                HSAs.append(analysis["HSAofBuildingFacade"])
                fHSAs.append(analysis["FinHSA"])
                VSAs.append(analysis["VSAofBuildingFacade"])
                fVSAs.append(analysis["FinVSA"])
        current += timedelta(minutes=30)

    # st.write All Variables
    if show_intermediate:
        st.markdown("### INPUTS ###")
        st.write("Latitude:", Latitude)
        st.write("Longitude:", Longitude)
        st.write("Year:", Year)

        #Single day - save for mobile app
        '''
        st.write("Month:", Month)
        st.write("Day:", Day)
        st.write("Hour:", Hour)
        st.write("Minute:", Minute)
        '''

        st.write("Timezone:", Timezone)
        st.write("AngleFinfromSouth:", AngleFinfromSouth)
        st.write("AngleFacadefromSouth:", AngleFacadefromSouth)
        st.write("StartMonth:", StartMonth)
        st.write("StartDay:", StartDay)
        st.write("EndMonth:", EndMonth)
        st.write("EndDay:", EndDay)
        st.write("StartTime:", StartTime)
        st.write("EndTime:", EndTime)

        st.markdown("### BUILDING ORIENTATION ###")
        st.write("ReformattedWallAngle:", ReformattedWallAngle)
        st.write("ReformattedFinAngle:", ReformattedFinAngle)
        st.write("FinAzimuth:", FinAzimuth)

        #Single day - save for mobile app
        '''
        st.markdown("### DATE / TIME ###")
        st.write("Date:", solar["Date"])
        st.write("Time:", solar["Time"])
        st.write("JulianDay:", solar["JulianDay"])
        st.write("JulianCentury:", solar["JulianCentury"])

        st.markdown("### INTERMEDIATE STUFF ###")
        st.write("GeomMeanLongSun:", solar["GeomMeanLongSun"])
        st.write("GeomMeanAnomSun:", solar["GeomMeanAnomSun"])
        st.write("EccentEarthOrbit:", solar["EccentEarthOrbit"])
        st.write("SunEqofCtr:", solar["SunEqofCtr"])
        st.write("SunTrueLong:", solar["SunTrueLong"])
        st.write("SunTrueAnom:", solar["SunTrueAnom"])
        st.write("SunRadVector:", solar["SunRadVector"])
        st.write("SunAppLong:", solar["SunAppLong"])
        st.write("MeanObliqEcliptic:", solar["MeanObliqEcliptic"])
        st.write("ObliqCorr:", solar["ObliqCorr"])
        st.write("SunRtAscen:", solar["SunRtAscen"])
        st.write("SunDeclin:", solar["SunDeclin"])
        st.write("vary:", solar["vary"])
        st.write("EqofTime:", solar["EqofTime"])
        st.write("HASunrise:", solar["HASunrise"])
        st.write("SolarNoon:", solar["SolarNoon"])
        st.write("SunriseTime:", solar["SunriseTime"])
        st.write("SunsetTime:", solar["SunsetTime"])
        st.write("SunlightDuration:", solar["SunlightDuration"])
        st.write("TrueSolarTime:", solar["TrueSolarTime"])
        st.write("HourAngle:", solar["HourAngle"])
        st.write("SolarZenithAngle:", solar["SolarZenithAngle"])
        st.write("SolarAltitudeAngle:", solar["SolarAltitudeAngle"])
        st.write("AppAtmosphericRefraction:", solar["AppAtmosphericRefraction"])
        st.write("SolarElevationcorrected:", solar["SolarElevationcorrected"])
        st.write("SolarAzimuthAngle:", solar["SolarAzimuthAngle"])

        st.markdown("### OVERHEATING ANALYSIS ###")
        st.write("OverheatPeriodAnalysis:", overheat["OverheatPeriodAnalysis"])
        st.write("HSAofBuildingFacade:", overheat["HSAofBuildingFacade"])
        st.write("VSAofBuildingFacade:", overheat["VSAofBuildingFacade"])
        st.write("FinHSA:", overheat["FinHSA"])
        st.write("FinVSA:", overheat["FinVSA"])
        '''

        st.markdown("### RELEVANT RANGE ###")
        st.write("Relevant timestamps:", len(relevant_altitudes))
        st.write("HSA Overheat MAX:", np.max(HSAs))
        st.write("HSA Overheat MIN:", np.min(HSAs))
        st.write("HSA Overheat MEDIAN:", np.median(HSAs))
        st.write("VSA Overheat MAX:", np.max(VSAs))
        st.write("VSA Overheat MIN:", np.min(VSAs))
        st.write("VSA Overheat MEDIAN:", np.median(VSAs))
        st.write("FIN HSA Overheat MAX:", np.max(fHSAs))
        st.write("FIN HSA Overheat MIN:", np.min(fHSAs))
        st.write("FIN HSA Overheat MEDIAN:", np.median(fHSAs))
        st.write("FIN VSA Overheat MAX:", np.max(fVSAs))
        st.write("FIN VSA Overheat MIN:", np.min(fVSAs))
        st.write("FIN VSA Overheat MEDIAN:", np.median(fVSAs))

    if HSAOverHeatPeriod == "max":
        vsep = np.max(HSAs)
        vse = np.max(fHSAs)
    elif HSAOverHeatPeriod == "median":
        vsep = np.median(HSAs)
        vse = np.median(fHSAs)
    else:
        vsep = np.min(HSAs)
        vse = np.min(fHSAs)
    if VSAOverHeatPeriod == "max":
        hsep = np.max(VSAs)
    elif HSAOverHeatPeriod == "median":
        hsep = np.median(VSAs)
    else:
        hsep = np.min(VSAs)

    st.markdown("### SHADING DESIGN RESULTS ###")
    st.write("Vertical Shading element perpendicular to wall:", vsep)
    st.write("Horizontal Shading element perpendicular to wall:", hsep)
    st.write("Vertical Shading element angle to wall:", vse)

    #Single day - save for mobile app
    '''
    st.write("Vertical Shading element:", overheat["HSAofBuildingFacade"])
    st.write("Horizontal Shading element:", overheat["VSAofBuildingFacade"])
    st.write("Vertical Shading element angle to wall:", overheat["FinHSA"])
    '''

if st.button("Calculate"):
    StartTime = time(StartHour, StartMinute)
    EndTime = time(EndHour, EndMinute)
    calculate()
show_intermediate = st.checkbox("Show intermediate calculations")