import streamlit as st
from serpapi.google_search import GoogleSearch

class ResearchAgent:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_company_info(self, company_name):
        params = {
            "engine": "google",
            "q": f"{company_name} company overview",
            "api_key": self.api_key
        }
        search = GoogleSearch(params)
        results = search.get_dict()

        company_summary = results.get("organic_results", [{}])[0].get("snippet", "No summary found.")
        industry = results.get("related_questions", [{}])[0].get("question", "No industry found.")
        key_offerings = results.get("related_questions", [{}])[1].get("question", "No offerings found.")
        sector = results.get("related_questions", [{}])[2].get("question", "No sector found.")

        return {
            "summary": company_summary,
            "industry": industry,
            "key_offerings": key_offerings,
            "sector": sector
        }


class SuggestionAgent:
    def __init__(self, api_key):
        self.api_key = api_key

    def suggest_use_cases(self, company_info):
        suggestions = [
            "Automate customer service with chatbots.",
            "Utilize predictive analytics for sales forecasting.",
            "Implement recommendation systems for personalized marketing."
        ]
        return suggestions


class AssetCollectionAgent:
    def __init__(self, api_key):
        self.api_key = api_key

    def search_datasets(self, use_cases):
        datasets = []
        for use_case in use_cases:
            params = {
                "engine": "google",
                "q": f"{use_case} dataset",
                "api_key": self.api_key
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            datasets.append({
                "use_case": use_case,
                "links": [result.get("link") for result in results.get("organic_results", [])]
            })
        return datasets


def main():
    st.title("Company Overview and AI Use Case Suggestion")

    api_key = st.text_input("Enter your SerpApi API Key:", type="password")
    company_name = st.text_input("Enter the company name:")

    if st.button("Get Company Info"):
        if api_key and company_name:
            research_agent = ResearchAgent(api_key)
            suggestion_agent = SuggestionAgent(api_key)
            asset_collection_agent = AssetCollectionAgent(api_key)

            # Research phase
            company_info = research_agent.get_company_info(company_name)
            st.subheader("Company Information:")
            st.write(company_info)

            # Suggestion phase
            use_cases = suggestion_agent.suggest_use_cases(company_info)
            st.subheader("Suggested Use Cases:")
            for use_case in use_cases:
                st.write(f"- {use_case}")

            # Asset collection phase
            datasets = asset_collection_agent.search_datasets(use_cases)
            st.subheader("Relevant Datasets:")
            for dataset in datasets:
                st.write(f"Use Case: {dataset['use_case']}")
                for link in dataset['links']:
                    st.write(f"  - {link}")
        else:
            st.error("Please enter both your API key and the company name.")

if __name__ == "__main__":
    main()
