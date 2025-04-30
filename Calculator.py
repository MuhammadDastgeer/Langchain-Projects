import streamlit as st
import datetime

# --- Session History ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- Page Title ---
st.set_page_config(page_title="NeuroCalc AI", page_icon="🧮")

st.title("NeuroCalc AI😎")
st.caption("No stress, just press and get the answer 🚀")

# --- Time-based Greeting ---
hour = datetime.datetime.now().hour
if hour < 12:
    st.info("🌅 Good Morning!")
elif hour < 18:
    st.info("☀️ Good Afternoon!")
else:
    st.info("🌙 Good Evening!")

# --- Menu ---
option = st.sidebar.radio("📘 Choose Function", [
    "Basic Calculator",
    "Age Calculator",
    "Unit Converter",
    "Calculation History",
    "Percentage Calculator",
    "Date Difference Calculator",
])

# --- Basic Calculator ---
if option == "Basic Calculator":
    st.subheader("🔢 Basic Calculator")
    num1 = st.number_input("Enter first number:", step=0.1, format="%.1f")
    operator = st.selectbox("Choose operator:", ["+", "-", "*", "/"])
    num2 = st.number_input("Enter second number:", step=0.1, format="%.1f")
    
    if st.button("Calculate"):
        result = None
        if operator == "+":
            result = num1 + num2
        elif operator == "-":
            result = num1 - num2
        elif operator == "*":
            result = num1 * num2
        elif operator == "/":
            if num2 != 0:
                result = num1 / num2
            else:
                st.error("Division by zero is not allowed!")
        
        if result is not None:
            output = f"{num1} {operator} {num2} = {result}"
            st.success(f"✅ Result: {result}")
            st.session_state.history.append(output)

# --- Age Calculator ---
elif option == "Age Calculator":
    st.subheader("🎂 Age Calculator")
    birth_year = st.number_input("Enter your birth year:", step=1, format="%d")
    if st.button("Find My Age"):
        current_year = datetime.datetime.now().year
        age = current_year - birth_year
        st.success(f"Aapki age hai: {age} saal 😄")
        st.session_state.history.append(f"Age calculated from year {birth_year} = {age} years")

# --- Unit Converter ---
elif option == "Unit Converter":
    st.subheader("📏 Unit Converter")
    converter = st.selectbox("Choose conversion type:", [
        "Inches to Centimeters",
        "Fahrenheit to Celsius",
        "Kilograms to Pounds"
    ])

    value = st.number_input("Enter value:", step=0.1, format="%.2f")

    if st.button("Convert"):
        result = None
        if converter == "Inches to Centimeters":
            result = value * 2.54
            unit = "cm"
        elif converter == "Fahrenheit to Celsius":
            result = (value - 32) * 5/9
            unit = "°C"
        elif converter == "Kilograms to Pounds":
            result = value * 2.20462
            unit = "lbs"
        st.success(f"✅ Converted: {result:.2f} {unit}")
        st.session_state.history.append(f"{value} converted via '{converter}' = {result:.2f} {unit}")

# --- History Viewer ---
elif option == "Calculation History":
    st.subheader("📜 History Log")
    if not st.session_state.history:
        st.info("No calculations yet!")
    else:
        for i, item in enumerate(st.session_state.history[::-1], 1):
            st.write(f"{i}. {item}")

# --- Percentage Calculator ---
elif option == "Percentage Calculator":
    st.subheader("📊 Percentage Calculator")
    base = st.number_input("Enter the base value (e.g. 100):", step=1.0)
    percent = st.number_input("Enter the percentage (e.g. 15):", step=1.0)
    if st.button("Calculate Percentage"):
        result = (base * percent) / 100
        st.success(f"✅ {percent}% of {base} is {result}")
        st.session_state.history.append(f"{percent}% of {base} = {result}")

# --- Date Difference Calculator ---
elif option == "Date Difference Calculator":
    st.subheader("📆 Date Difference Calculator")
    st.caption("🎉 Apki shadi kab hui thi? Ya koi aur yaadgar din? Dekhte hain kitne din guzre 😁")

    date1 = st.date_input("Enter first date:")
    date2 = st.date_input("Enter second date:")

    if st.button("Calculate Date Difference"):
        diff = abs((date2 - date1).days)
        st.success(f"📅 Difference between the two dates is: {diff} days")
        st.session_state.history.append(f"Date difference between {date1} and {date2} = {diff} days")
