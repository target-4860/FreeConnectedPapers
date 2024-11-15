import time
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional

import requests


class PaperFetcher:
    """Class to fetch paper information from arXiv and Semantic Scholar"""

    def __init__(self):
        self.arxiv_base_url = "http://export.arxiv.org/api/query"
        self.semantic_scholar_base_url = "https://api.semanticscholar.org/graph/v1"
        self.s2_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def search_arxiv(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search arXiv for papers using their API

        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return

        Returns:
            list: List of dictionaries containing paper details
        """
        params = {
            "search_query": query,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending",
        }

        try:
            response = requests.get(self.arxiv_base_url, params=params)
            response.raise_for_status()

            # Parse the XML response
            root = ET.fromstring(response.content)
            namespace = {"atom": "http://www.w3.org/2005/Atom"}

            papers = []
            for entry in root.findall("atom:entry", namespace):
                paper = {
                    "title": entry.find("atom:title", namespace).text.strip(),
                    "authors": [
                        author.find("atom:name", namespace).text
                        for author in entry.findall("atom:author", namespace)
                    ],
                    "summary": entry.find("atom:summary", namespace).text.strip(),
                    "published": entry.find("atom:published", namespace).text,
                    "arxiv_id": entry.find("atom:id", namespace)
                    .text.split("/")[-1]
                    .split("v")[0],  # Remove version number
                    "pdf_link": next(
                        (
                            link.get("href")
                            for link in entry.findall("atom:link", namespace)
                            if link.get("title") == "pdf"
                        ),
                        None,
                    ),
                }
                papers.append(paper)

            return papers

        except requests.exceptions.RequestException as e:
            print(f"Error making request to arXiv: {e}")
            return []
        except ET.ParseError as e:
            print(f"Error parsing XML response: {e}")
            return []

    def get_semantic_scholar_data(self, arxiv_id: str) -> Optional[Dict]:
        """
        Get citation data from Semantic Scholar API

        Args:
            arxiv_id (str): arXiv ID of the paper

        Returns:
            dict: Paper details including citations
        """
        # Construct the API URL for paper details
        paper_url = f"{self.semantic_scholar_base_url}/paper/arXiv:{arxiv_id}"

        # Define the fields we want to retrieve
        fields = (
            "title,authors,year,url,abstract,citations,references,citationCount,referenceCount"
        )

        params = {"fields": fields, "limit": 15}  # Limit citations and references to 5 each

        max_retries = 5
        retry_count = 0

        while retry_count < max_retries:
            try:
                response = requests.get(paper_url, headers=self.s2_headers, params=params)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429 and retry_count < max_retries - 1:
                    retry_count += 1
                    time.sleep(0.5)  # Wait half second before retrying
                    continue
                print(f"Error fetching Semantic Scholar data: {e}")
                return None
            except requests.exceptions.RequestException as e:
                print(f"Error fetching Semantic Scholar data: {e}")
                return None

    def get_paper_details(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Get complete paper details including citations

        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return

        Returns:
            list: List of papers with complete details
        """
        # First get arXiv results
        arxiv_papers = self.search_arxiv(query, max_results)
        detailed_papers = []

        for paper in arxiv_papers:
            print(f"\nFetching citation data for: {paper['title']}")

            # Get Semantic Scholar data
            s2_data = self.get_semantic_scholar_data(paper["arxiv_id"])

            if s2_data:
                # Combine data from both sources
                detailed_paper = {
                    **paper,
                    "citation_count": s2_data.get("citationCount", 0),
                    "reference_count": s2_data.get("referenceCount", 0),
                    "citations": [
                        {
                            "title": citation.get("title", ""),
                            "authors": [
                                author.get("name", "") for author in citation.get("authors", [])
                            ],
                            "year": citation.get("year", ""),
                            "url": citation.get("url", ""),
                        }
                        for citation in s2_data.get("citations", [])
                    ],
                    "references": [
                        {
                            "title": ref.get("title", ""),
                            "authors": [
                                author.get("name", "") for author in ref.get("authors", [])
                            ],
                            "year": ref.get("year", ""),
                            "url": ref.get("url", ""),
                        }
                        for ref in s2_data.get("references", [])
                    ],
                }
                detailed_papers.append(detailed_paper)
            else:
                detailed_papers.append(paper)

        return detailed_papers


def print_paper_details(papers: List[Dict]) -> None:
    """Pretty print paper details"""
    for i, paper in enumerate(papers, 1):
        print(f"\n{'='*100}")
        print(f"Paper {i}:")
        print(f"{'='*100}")
        print(f"Title: {paper['title']}")
        print(f"Authors: {', '.join(paper['authors'])}")
        print(f"Published: {paper['published']}")
        print(f"arXiv ID: {paper['arxiv_id']}")
        print(f"PDF Link: {paper['pdf_link']}")
        print(f"\nSummary: {paper['summary'][:300]}...")

        # Print citation metrics if available
        if "citation_count" in paper:
            print(f"\nCitation count: {paper['citation_count']}")
            print(f"Reference count: {paper['reference_count']}")

            # Print top citing papers
            if paper["citations"]:
                print("\nTop citing papers:")
                for j, citation in enumerate(paper["citations"], 1):
                    print(f"\n{j}. {citation['title']}")
                    print(f"   Authors: {', '.join(citation['authors'])}")
                    print(f"   Year: {citation['year']}")
                    print(f"   URL: {citation['url']}")

            # Print top referenced papers
            if paper["references"]:
                print("\nTop referenced papers:")
                for j, ref in enumerate(paper["references"], 1):
                    print(f"\n{j}. {ref['title']}")
                    print(f"   Authors: {', '.join(ref['authors'])}")
                    print(f"   Year: {ref['year']}")
                    print(f"   URL: {ref['url']}")


if __name__ == "__main__":
    # Initialize fetcher
    fetcher = PaperFetcher()

    # Search for "Attention is all you need"
    query = 'ti:"Attention is all you need"'

    print("Searching for papers and fetching citation data...")
    papers = fetcher.get_paper_details(query)

    # Print results
    if papers:
        print_paper_details(papers)
    else:
        print("No papers found or error occurred during search.")
