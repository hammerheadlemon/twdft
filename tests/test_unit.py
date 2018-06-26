from twdft.twdft import _clean_site_name_for_path as clean_site_name


def test_clean_bad_site_names(bad_site_names):
    site_name = bad_site_names
    awful = [
        "awful-site-name-with-space",
        "bad-and-badder-site",
        "test-site-1",
    ]
    assert clean_site_name(site_name) in awful
