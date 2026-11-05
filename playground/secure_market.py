"""Marlowe v6 user interface; all data operations go through the authenticated TLS API.
Run: uv run --extra apps streamlit run playground/secure_market.py
CPU: seconds for frozen inputs. Prepare identities and start serve_tier5.py first.
"""

import ssl

import httpx
import streamlit as st

from common.settings import cache_dir


def main():
    st.title("Marlowe Search v6")
    st.caption("Private seller search · secure local connection")
    token = st.sidebar.text_input("Access token", type="password")
    flow = st.sidebar.radio(
        "Explore", ["Products", "Help center", "Similar items", "Listing review", "Photos"]
    )
    st.sidebar.caption("Your access token determines the seller account and permissions.")
    body = {}
    method = "POST"
    if flow == "Products":
        query = st.selectbox("Saved search", [f"q{i:03}" for i in [0, 1, 2, 3, 4, 6, 7, 8, 9]])
        endpoint, body = "/search", {"query_id": query, "k": 5}
    elif flow == "Help center":
        st.caption("The help articles are public marketplace policies.")
        endpoint, body = (
            "/help",
            {"question_id": st.selectbox("Question", [f"rag-{i:03}" for i in range(5)])},
        )
    elif flow == "Similar items":
        product = st.text_input("Your listing ID", "p0000000")
        endpoint, method = "/similar/" + product, "GET"
    elif flow == "Listing review":
        endpoint = "/duplicates"
        body = {
            "first": st.text_input("First listing", "p0000000"),
            "second": st.text_input("Second listing", "p0000300"),
            "threshold": st.slider("Similarity threshold", 0.0, 1.0, 0.8),
        }
    else:
        endpoint, body = (
            "/photos",
            {"product_id": st.text_input("Your photo listing ID", "p0000000"), "k": 5},
        )
    if st.button("Search", disabled=not token):
        try:
            context = ssl.create_default_context(
                cafile=str(cache_dir() / "tier5/runtime/tls/ca.pem")
            )
            with httpx.Client(
                base_url="https://localhost:8443",
                verify=context,
                timeout=60,
                headers={"Authorization": "Bearer " + token},
            ) as client:
                response = client.request(method, endpoint, json=body if method == "POST" else None)
                if response.is_success:
                    st.json(response.json()["data"])
                else:
                    st.error(response.json().get("detail", "Request unavailable"))
        except (OSError, httpx.HTTPError):
            st.error(
                "The secure local service is unavailable. Start the service and check its certificate."
            )


if __name__ == "__main__":
    main()
