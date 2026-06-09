import os

from companion_link import companion_site_base, customer_url, embed_url


def test_customer_url_with_employer(monkeypatch):
    monkeypatch.setenv("ROLLOVER_COMPANION_URL", "http://localhost:3000")
    url = customer_url(employer="Target", provider="Alight Solutions")
    assert url.startswith("http://localhost:3000/customer?")
    assert "employer=Target" in url
    assert "provider=Alight" in url


def test_embed_url_strips_path_from_base(monkeypatch):
    monkeypatch.setenv("ROLLOVER_COMPANION_URL", "https://demo.example.com/customer")
    assert companion_site_base() == "https://demo.example.com"
    assert embed_url(employer="FedEx").startswith("https://demo.example.com/embed?")
