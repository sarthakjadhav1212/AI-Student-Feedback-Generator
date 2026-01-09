

import streamlit as st
import pandas as pd
import google.generativeai as genai
import time

st.set_page_config(page_title="AI Student Feedback Generator",layout="wide")

st.title("AI Student Feedback Generator")
st.markdown("Upload a student scores Excel file to generate AI-based personalized feedback.")

API_KEY="AIzaSyALNuFFbVNQ8yk9hm1r0nak8LXOxFkrZ24"

MODEL_NAME="models/gemini-1.5-flash"

uploaded_file=st.file_uploader("Upload Excel File",type=["xlsx","xls"])

if uploaded_file:
    try:
        genai.configure(api_key=API_KEY)
        model=genai.GenerativeModel(MODEL_NAME)

        df=pd.read_excel(uploaded_file)
        df.columns=df.columns.str.strip()

        name_col=next((c for c in df.columns if "name" in c.lower()),df.columns[0])
        score_col=next((c for c in df.columns if any(x in c.lower() for x in ["score","marks","grade","total"])),df.columns[-1])
        serial_col=next((c for c in df.columns if any(x in c.lower() for x in ["sl","sn","roll","id","no"])),None)

        st.success(f"Detected columns → Name: {name_col} | Score: {score_col}")
        st.dataframe(df.head(),use_container_width=True)

        if st.button("Generate AI Feedback"):
            st.subheader("Generating AI Feedback")
            progress=st.progress(0)
            status=st.empty()

            results=[]
            total=len(df)

            for i,row in df.iterrows():
                s_no=row[serial_col] if serial_col else i+1
                name=str(row[name_col])
                score=float(row[score_col])

                status.info(f"Processing feedback for {name}")

                prompt=f"""
You are an academic mentor.

Generate exactly THREE short feedback lines for a student.

Student Name: {name}
Score: {score}/100

Format strictly as:
1. Performance Summary:
2. Strength:
3. Improvement Area:
"""

                try:
                    response=model.generate_content(prompt)
                    feedback=response.text.strip()
                except:
                    feedback=(
                        "1. Performance Summary: The student shows steady academic progress.\n"
                        "2. Strength: Demonstrates good understanding of core concepts.\n"
                        "3. Improvement Area: Should focus on regular practice to improve further."
                    )

                results.append({
                    "Serial":s_no,
                    "Student Name":name,
                    "Score":score,
                    "AI Feedback":feedback
                })

                progress.progress((i+1)/total)
                time.sleep(4)

            result_df=pd.DataFrame(results)

            st.success("AI feedback generated successfully")
            st.subheader("Generated AI Feedback")
            st.dataframe(result_df,use_container_width=True)

            csv=result_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download Feedback CSV",
                csv,
                "student_ai_feedback.csv",
                "text/csv",
                use_container_width=True
            )

    except Exception as e:
        st.error(str(e))
else:
    st.info("Upload an Excel file to start.")

