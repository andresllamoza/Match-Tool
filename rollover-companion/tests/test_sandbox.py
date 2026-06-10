"""Legacy sandbox UI helpers — routing card HTML."""

from sandbox.ui import channel


def test_routing_security_card_renders_fbo():
    html = channel.routing_security_card("PensionBee FBO Avery Quinn", "PO Box 72, New York, NY 10272")
    assert "Critical" in html
    assert "PensionBee FBO Avery Quinn" in html
