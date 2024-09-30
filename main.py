import os
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
from langchain_core.prompts.prompt import PromptTemplate
from langchain_openai import ChatOpenAI

# Load environment variables from the .env file
load_dotenv()

# Allowed classification categories as per prompt
ALLOWED_CLASSIFICATIONS = ["Functional", "Marketing", "Performance", "Essential"]

def get_cookie_info_from_openai(cookie_name):
    # Define the prompt with detailed explanations of each variable
    summary_template = f"""
    Given the cookie name "{cookie_name}", provide one or more information about the cookie in the following format:
    
    Cookie Name: <cookie_name>
    Static/Dynamic: <static_or_dynamic>
    Static Pattern: <static_pattern>
    Dynamic Part: <dynamic_part>
    Vendor: <vendor>
    Classification: <classification>
    Initiator: <initiator>
    Duration: <duration>
    Market: <market>
    Ownership: <ownership>
    Description: <description>
    
    Make sure you provide information that user has asked.
    
    Please follow the detailed explanations for each variable:
    
    1. **`cookie_name`**: The exact name of the cookie, uniquely identifying it. This name is how the cookie is stored in the user's browser (e.g., "dtCookie", "sessionId").

    2. **`static_or_dynamic`**: Identify if the cookie name is static or dynamic. If the cookie contains a part that is subject to change (like a session ID), classify it as "Dynamic", otherwise "Static".
    
    3. **`static_pattern`**: If the cookie name is dynamic, provide a pattern representation by using `*` to replace the dynamic part (e.g., "_ga_*" for "_ga_GYEG29ES6L").
    
    4. **`dynamic_part`**: If the cookie is dynamic, extract and provide the portion of the cookie name that changes (e.g., "GYEG29ES6L" for "_ga_GYEG29ES6L").

    5. **`vendor`**: The company, organization, or service responsible for creating and managing the cookie. This is the entity that sets and controls the cookie's usage (e.g., "Dynatrace", "Google Analytics", "Facebook").

    6. **`classification`**: The purpose or functional category of the cookie. Please choose one of the following categories:
       - **Functional**: Helps enhance website functionality and user experience but is not essential.
       - **Marketing**: Used for tracking visitors across websites to enable targeted advertising.
       - **Performance**: Collects information about how users interact with a site to improve performance.
       - **Essential**: Strictly necessary for the basic operations of the site, like security or session management.

    7. **`initiator`**: The source, tool, or script that set or triggered the setting of the cookie. This could be a software tool, a monitoring script, or a third-party library (e.g., "Dynatrace Monitoring Script", "Google Analytics JS", "Website's own session management script").

    8. **`duration`**: The lifespan or expiry period of the cookie. This defines how long the cookie will remain on the user's device before being automatically deleted. Values could include:
       - **"Session"**: The cookie lasts only for the duration of the browser session and is deleted when the session ends.
       - **A specific time frame**: The cookie persists for a defined duration, such as "30 days", "6 months", or "1 year".

    9. **`market`**: The geographical scope or specific user segment where the cookie is applicable or used. Specify if it is:
       - **"Global"**: Used across all regions where the site operates.
       - **"EU Only"**: Only applicable within the European Union.
       - **"US Market"**: Specific to users in the United States.
       - Any other specific regional or market-based scope as applicable.

    10. **`ownership`**: Specifies whether the cookie is owned by the domain visited by the user (first-party) or by a different domain (third-party). Options are:
       - **"1st Party"**: The cookie is set directly by the website the user is visiting.
       - **"3rd Party"**: The cookie is set by a different domain, typically for cross-site tracking or third-party services like ads.

    11. **`description`**: A comprehensive explanation of what the cookie does, its purpose, and any specific functions it serves. Mention if it collects any user data, tracks user behavior, stores session information, or is used for personalization, analytics, or advertising.
    """

    summary_prompt_template = PromptTemplate(input_variables="cookie_name", template=summary_template)
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    chain = summary_prompt_template | llm 
    res = chain.invoke(input={"cookie_name": cookie_name})
    
    return res.content

def filter_classification(value):
    """Ensure the classification is one of the allowed values."""
    for allowed in ALLOWED_CLASSIFICATIONS:
        if allowed.lower() in value.lower():
            return allowed
    return "Other"  # If no match, default to "Other"

# Main code for Streamlit app
if __name__ == "__main__":
    st.title("Cookie Information Finder")

    # Container to display response
    response_container = st.container()

    # Input container fixed at the bottom
    input_container = st.container()

    # User input section at the bottom
    with input_container:
        user_input = st.text_input("Enter a cookie name below to get details:", "", key="user_input_box")
        submit_button = st.button("Get Cookie Details")

    # Display cookie information above input box
    if submit_button and user_input.strip():
        cookie_info = get_cookie_info_from_openai(user_input.strip())

        # Parse the response into a dictionary
        cookie_data = {}
        description_text = ""
        for line in cookie_info.split("\n"):
            if ": " in line:
                key, value = line.split(": ", 1)
                key = key.strip()
                value = value.strip()
                
                # Filter classification to ensure it matches allowed values
                if key.lower() == "classification":
                    value = filter_classification(value)
                
                if key.lower() == "description":
                    description_text = value
                else:
                    cookie_data[key] = value

        # Display response in the container above the input
        with response_container:
            st.subheader("Cookie Description")
            st.markdown(f"<div style='padding: 10px; background-color: #f0f0f0; border-radius: 8px;'>{description_text}</div>", unsafe_allow_html=True)

            # Transform data to display vertically
            df = pd.DataFrame(cookie_data.items(), columns=['Attribute', 'Value'])

            # Change the index to start from 1
            df.index += 1

            # Apply center alignment and add scrollable area
            st.subheader("Cookie Information")
            st.dataframe(
                df.style.set_table_styles(
                    [
                        {'selector': 'th', 'props': [('background-color', '#0e3d66'), ('color', 'white'), ('text-align', 'center'), ('font-weight', 'bold')]},
                        {'selector': 'td', 'props': [('text-align', 'center')]}
                    ]
                ),
                use_container_width=True,
                height=400  # Set a fixed height for scrolling
            )
