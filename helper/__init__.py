

def get_all_links_from_source(source: str, base_url: str) -> list[tuple[str, str]]:
    """
    Extract all links from the given HTML source code.

    Args:
        source (str): The HTML source code as a string.
        base_url (str): The base URL to resolve relative links.

    Returns:
        list[tuple[str, str]]: A list of tuples containing link text and href.
    """
    from urllib.parse import urljoin
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(source, "html.parser")
    links = soup.find_all("a")

    link_list = []
    for link in links:
        text = link.get_text(strip=True)
        href = link.get("href")
        if href and text:
            if href == "#":
                continue
            href = urljoin(base_url, href)  # Make sure href is absolute
            link_list.append((text, href))

    return link_list
