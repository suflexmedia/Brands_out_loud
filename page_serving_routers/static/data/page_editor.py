import re
import os

def extract_data(marker_text, page_data):
    escaped_marker = re.escape(marker_text)
    pattern = f"{escaped_marker}(.*?){escaped_marker}"
    matches = re.findall(pattern, page_data, re.DOTALL)
    if matches:
        return matches[0]
    else:
        return None 




def get_homepage_data():
    print(os.getcwd())
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, '..', '..', 'templates', 'homepage.html')
    with open(file_path, encoding="utf8") as f:
        xx = f.read()
    home_page_data = {
        "homepage": {
            "section1": {
                "title": "SECTION 1",
                "description": "This is the top section of the homepage, featuring the main content and highlighted posts in various positions.",
                "template_image": "static/images/ADMIN_PANEL/homepage/section1.png",
                "popup_fields":{"MAIN_CONTENT_SECTION": {
                                "title": extract_data("<!-- <section_1_title> -->", xx),
                                "date": extract_data("<!-- <section_1_date> -->", xx),
                                "publisher": extract_data("<!-- <section_1_publisher> -->", xx),
                                "image": extract_data("<section_1_image>", xx).replace("bg-[url(", "").replace(")]", "").strip() if extract_data("<section_1_image>", xx) else None
                                },
                                "TOP RIGHT SECTION": {
                                    "post_1": {
                                        "title": extract_data("<!-- <section_1_top_right_section_title1> -->", xx),
                                        "date": extract_data("<!-- <section_1_top_right_section_date1> -->", xx),
                                        "publisher": extract_data("<!-- <section_1_top_right_section_publisher1> -->", xx),
                                        "image": extract_data("<section_1_top_right_image1>", xx).replace("bg-[url(", "").replace(")]", "").strip() if extract_data("<section_1_top_right_image1>", xx) else None
                                    },
                                    "post_2": {
                                        "title": extract_data("<!-- <section_1_top_right_section_title2> -->", xx),
                                        "date": extract_data("<!-- <section_1_top_right_section_date2> -->", xx),
                                        "publisher": extract_data("<!-- <section_1_top_right_section_publisher2> -->", xx),
                                        "image": extract_data("<section_1_top_right_image2>", xx).replace("bg-[url(", "").replace(")]", "").strip() if extract_data("<section_1_top_right_image2>", xx) else None
                                    }
                                },
                                "LEFT BOTTOM SECTION": {
                                        "title": extract_data("<!-- <section_1_left_bottom_section_title1> -->", xx),
                                        "date": extract_data("<!-- <section_1_left_bottom_section_date1> -->", xx),
                                        "publisher": extract_data("<!-- <section_1_left_bottom_section_publisher1> -->", xx),
                                        "image": extract_data("<section_1_left_bottom_image1>", xx).replace("bg-[url(", "").replace(")]", "").strip() if extract_data("<section_1_left_bottom_image1>", xx) else None
                                }
                        }
            },
            "section2": {
                "title": "SECTION 2",
                "description": "This section typically highlights a single featured article or piece of content.",
                "template_image": "static/images/ADMIN_PANEL/homepage/section2and4.png",
                "popup_fields":
                    {"MAIN_CONTENT_SECTION": {
                                "title": extract_data("<!-- <section_2_title> -->", xx),
                                "date": extract_data("<!-- <section_2_date> -->", xx),
                                "publisher": extract_data("<!-- <section_2_publisher> -->", xx),
                                "image": extract_data("<section_2_image>", xx).replace("bg-[url(", "").replace(")]", "").strip() if extract_data("<section_2_image>", xx) else None
                            }
                        }
                },
            "section3": {
                "title": "SECTION 3",
                "description": "This section is designed to showcase a primary piece of content, often with a title and descriptive text.",
                "template_image": "static/images/ADMIN_PANEL/homepage/section3.png",
                "popup_fields":{"MAIN_CONTENT_SECTION": {
                                "title": extract_data("<!-- <section_3_title> -->", xx),
                                "description": extract_data("<!-- <section_3_description> -->", xx),
                    }
                },
            },
            "section4": {
                "title": "SECTION 4",
                "description": "Similar to Section 2, this area is for featuring another significant article or content block.",
                "template_image": "static/images/ADMIN_PANEL/homepage/section2and4.png",
                "popup_fields":{"MAIN_CONTENT_SECTION": {
                                "title": extract_data("<!-- <section_4_title> -->", xx),
                                "date": extract_data("<!-- <section_4_date> -->", xx),
                                "publisher": extract_data("<!-- <section_4_publisher> -->", xx),
                                "image": extract_data("<section_4_image>", xx).replace("bg-[url(", "").replace(")]", "").strip() if extract_data("<section_4_image>", xx) else None
                            }
                },
            },
            "section5": {
                "title": "SECTION 5",
                "description": "A multi-part section featuring a header, main content, and additional posts arranged in left and bottom subsections.",
                "template_image": "static/images/ADMIN_PANEL/homepage/section5and7.png",
                "popup_fields":{
                    "HEADER": extract_data("<!-- <section_5_header> -->", xx),
                    "MAIN_CONTENT_SECTION": {
                        "title": extract_data("<!-- <section_5_title> -->", xx),
                        "date": extract_data("<!-- <section_5_date> -->", xx),
                        "publisher": extract_data("<!-- <section_5_publisher> -->", xx),
                        "image": extract_data("<!-- <section_5_image> -->", xx).split('src="')[-1].split('"')[0] if extract_data("<!-- <section_5_image> -->", xx) and 'src="' in extract_data("<!-- <section_5_image> -->", xx) else None,
                        "alt_text": extract_data("<!-- <section_5_image> -->", xx).split('alt="')[-1].split('"')[0] if extract_data("<!-- <section_5_image> -->", xx) and 'alt="' in extract_data("<!-- <section_5_image> -->", xx) else None,
                        "time": extract_data("<!-- <section_5_time> -->", xx),
                        "category": extract_data("<!-- <section_5_category> -->", xx)
                    },
                    "LEFT SECTION": {
                        "post_1": {
                            "title": extract_data("<!-- <section_5_left_section_title1> -->", xx),
                            "date": extract_data("<!-- <section_5_left_section_date1> -->", xx),
                            "publisher": extract_data("<!-- <section_5_left_section_publisher1> -->", xx),
                            "image": extract_data("<!-- <section_5_left_section_image1> -->", xx).split('src="')[-1].split('"')[0] if extract_data("<!-- <section_5_left_section_image1> -->", xx) and 'src="' in extract_data("<!-- <section_5_left_section_image1> -->", xx) else None,
                            "alt_text": extract_data("<!-- <section_5_left_section_image1> -->", xx).split('alt="')[-1].split('"')[0] if extract_data("<!-- <section_5_left_section_image1> -->", xx) and 'alt="' in extract_data("<!-- <section_5_left_section_image1> -->", xx) else None,
                            "category": extract_data("<!-- <section_5_left_section_category1> -->", xx)
                        },
                        "post_2": {
                            "title": extract_data("<!-- <section_5_left_section_title2> -->", xx),
                            "date": extract_data("<!-- <section_5_left_section_date2> -->", xx),
                            "publisher": extract_data("<!-- <section_5_left_section_publisher2> -->", xx),
                            "image": extract_data("<!-- <section_5_left_section_image2> -->", xx).split('src="')[-1].split('"')[0] if extract_data("<!-- <section_5_left_section_image2> -->", xx) and 'src="' in extract_data("<!-- <section_5_left_section_image2> -->", xx) else None,
                            "alt_text": extract_data("<!-- <section_5_left_section_image2> -->", xx).split('alt="')[-1].split('"')[0] if extract_data("<!-- <section_5_left_section_image2> -->", xx) and 'alt="' in extract_data("<!-- <section_5_left_section_image2> -->", xx) else None,
                            "category": extract_data("<!-- <section_5_left_section_category2> -->", xx)
                        }
                    },
                    "BOTTOM SECTION": {
                        "post_1": {
                            "title": extract_data("<!-- <section_5_bottom_section_title1> -->", xx),
                            "date": extract_data("<!-- <section_5_bottom_section_date1> -->", xx),
                            "publisher": extract_data("<!-- <section_5_bottom_section_publisher1> -->", xx),
                            "image": extract_data("<!-- <section_5_bottom_section_image1> -->", xx).split('src="')[-1].split('"')[0] if extract_data("<!-- <section_5_bottom_section_image1> -->", xx) and 'src="' in extract_data("<!-- <section_5_bottom_section_image1> -->", xx) else None,
                            "alt_text": extract_data("<!-- <section_5_bottom_section_image1> -->", xx).split('alt="')[-1].split('"')[0] if extract_data("<!-- <section_5_bottom_section_image1> -->", xx) and 'alt="' in extract_data("<!-- <section_5_bottom_section_image1> -->", xx) else None,
                            "category": extract_data("<!-- <section_5_bottom_section_category1> -->", xx)
                        },
                        "post_2": {
                            "title": extract_data("<!-- <section_5_bottom_section_title2> -->", xx),
                            "date": extract_data("<!-- <section_5_bottom_section_date2> -->", xx),
                            "publisher": extract_data("<!-- <section_5_bottom_section_publisher2> -->", xx),
                            "image": extract_data("<!-- <section_5_bottom_section_image2> -->", xx).split('src="')[-1].split('"')[0] if extract_data("<!-- <section_5_bottom_section_image2> -->", xx) and 'src="' in extract_data("<!-- <section_5_bottom_section_image2> -->", xx) else None,
                            "alt_text": extract_data("<!-- <section_5_bottom_section_image2> -->", xx).split('alt="')[-1].split('"')[0] if extract_data("<!-- <section_5_bottom_section_image2> -->", xx) and 'alt="' in extract_data("<!-- <section_5_bottom_section_image2> -->", xx) else None,
                            "category": extract_data("<!-- <section_5_bottom_section_category2> -->", xx)
                        },
                        "post_3": {
                            "title": extract_data("<!-- <section_5_bottom_section_title3> -->", xx),
                            "date": extract_data("<!-- <section_5_bottom_section_date3> -->", xx),
                            "publisher": extract_data("<!-- <section_5_bottom_section_publisher3> -->", xx),
                            "image": extract_data("<!-- <section_5_bottom_section_image3> -->", xx).split('src="')[-1].split('"')[0] if extract_data("<!-- <section_5_bottom_section_image3> -->", xx) and 'src="' in extract_data("<!-- <section_5_bottom_section_image3> -->", xx) else None,
                            "alt_text": extract_data("<!-- <section_5_bottom_section_image3> -->", xx).split('alt="')[-1].split('"')[0] if extract_data("<!-- <section_5_bottom_section_image3> -->", xx) and 'alt="' in extract_data("<!-- <section_5_bottom_section_image3> -->", xx) else None,
                            "category": extract_data("<!-- <section_5_bottom_section_category3> -->", xx)
                        },
                        "post_4": {
                            "title": extract_data("<!-- <section_5_bottom_section_title4> -->", xx),
                            "date": extract_data("<!-- <section_5_bottom_section_date4> -->", xx),
                            "publisher": extract_data("<!-- <section_5_bottom_section_publisher4> -->", xx),
                            "image": extract_data("<!-- <section_5_bottom_section_image4> -->", xx).split('src="')[-1].split('"')[0] if extract_data("<!-- <section_5_bottom_section_image4> -->", xx) and 'src="' in extract_data("<!-- <section_5_bottom_section_image4> -->", xx) else None,
                            "alt_text": extract_data("<!-- <section_5_bottom_section_image4> -->", xx).split('alt="')[-1].split('"')[0] if extract_data("<!-- <section_5_bottom_section_image4> -->", xx) and 'alt="' in extract_data("<!-- <section_5_bottom_section_image4> -->", xx) else None,
                            "category": extract_data("<!-- <section_5_bottom_section_category4> -->", xx)
                        }
                    }
                },
            },
            "section6": {
                "title": "SECTION 6",
                "description": "This section is primarily for a large background image or visual banner.",
                "template_image": "static/images/ADMIN_PANEL/homepage/section6.png",
                "popup_fields":{
                    "picture": extract_data("<section_6_image>", xx).replace("bg-[url(", "").replace(")]", "").strip() if extract_data("<section_6_image>", xx) else None
                }
            },
            "section7": {
                "title": "SECTION 7",
                "description": "Another comprehensive section, similar to Section 5, with a header, main content, and multiple posts in left and bottom areas.",
                "template_image": "static/images/ADMIN_PANEL/homepage/section5and7.png",
                "popup_fields":{
                    "HEADER": extract_data("<!-- <section_7_header> -->", xx),
                    "MAIN_CONTENT_SECTION": {
                        "title": extract_data("<!-- <section_7_title> -->", xx),
                        "date": extract_data("<!-- <section_7_date> -->", xx),
                        "publisher": extract_data("<!-- <section_7_publisher> -->", xx),
                        "image": extract_data("<!-- <section_7_image> -->", xx).split('src="')[-1].split('"')[0] if extract_data("<!-- <section_7_image> -->", xx) and 'src="' in extract_data("<!-- <section_7_image> -->", xx) else None,
                        "alt_text": extract_data("<!-- <section_7_image> -->", xx).split('alt="')[-1].split('"')[0] if extract_data("<!-- <section_7_image> -->", xx) and 'alt="' in extract_data("<!-- <section_7_image> -->", xx) else None,
                        "time": extract_data("<!-- <section_7_time> -->", xx),
                        "category": extract_data("<!-- <section_7_category> -->", xx)
                    },
                    "LEFT SECTION": {
                        "post_1": {
                            "title": extract_data("<!-- <section_7_left_section_title1> -->", xx),
                            "date": extract_data("<!-- <section_7_left_section_date1> -->", xx),
                            "publisher": extract_data("<!-- <section_7_left_section_publisher1> -->", xx),
                            "image": extract_data("<!-- <section_7_left_section_image1> -->", xx).split('src="')[-1].split('"')[0] if extract_data("<!-- <section_7_left_section_image1> -->", xx) and 'src="' in extract_data("<!-- <section_7_left_section_image1> -->", xx) else None,
                            "alt_text": extract_data("<!-- <section_7_left_section_image1> -->", xx).split('alt="')[-1].split('"')[0] if extract_data("<!-- <section_7_left_section_image1> -->", xx) and 'alt="' in extract_data("<!-- <section_7_left_section_image1> -->", xx) else None,
                            "category": extract_data("<!-- <section_7_left_section_category1> -->", xx)
                        },
                        "post_2": {
                            "title": extract_data("<!-- <section_7_left_section_title2> -->", xx),
                            "date": extract_data("<!-- <section_7_left_section_date2> -->", xx),
                            "publisher": extract_data("<!-- <section_7_left_section_publisher2> -->", xx),
                            "image": extract_data("<!-- <section_7_left_section_image2> -->", xx).split('src="')[-1].split('"')[0] if extract_data("<!-- <section_7_left_section_image2> -->", xx) and 'src="' in extract_data("<!-- <section_7_left_section_image2> -->", xx) else None,
                            "alt_text": extract_data("<!-- <section_7_left_section_image2> -->", xx).split('alt="')[-1].split('"')[0] if extract_data("<!-- <section_7_left_section_image2> -->", xx) and 'alt="' in extract_data("<!-- <section_7_left_section_image2> -->", xx) else None,
                            "category": extract_data("<!-- <section_7_left_section_category2> -->", xx)
                        }
                    },
                    "BOTTOM SECTION": {
                        "post_1": {
                            "title": extract_data("<!-- <section_7_bottom_section_title1> -->", xx),
                            "date": extract_data("<!-- <section_7_bottom_section_date1> -->", xx),
                            "publisher": extract_data("<!-- <section_7_bottom_section_publisher1> -->", xx),
                            "image": extract_data("<!-- <section_7_bottom_section_image1> -->", xx).split('src="')[-1].split('"')[0] if extract_data("<!-- <section_7_bottom_section_image1> -->", xx) and 'src="' in extract_data("<!-- <section_7_bottom_section_image1> -->", xx) else None,
                            "alt_text": extract_data("<!-- <section_7_bottom_section_image1> -->", xx).split('alt="')[-1].split('"')[0] if extract_data("<!-- <section_7_bottom_section_image1> -->", xx) and 'alt="' in extract_data("<!-- <section_7_bottom_section_image1> -->", xx) else None,
                            "category": extract_data("<!-- <section_7_bottom_section_category1> -->", xx)
                        },
                        "post_2": {
                            "title": extract_data("<!-- <section_7_bottom_section_title2> -->", xx),
                            "date": extract_data("<!-- <section_7_bottom_section_date2> -->", xx),
                            "publisher": extract_data("<!-- <section_7_bottom_section_publisher2> -->", xx),
                            "image": extract_data("<!-- <section_7_bottom_section_image2> -->", xx).split('src="')[-1].split('"')[0] if extract_data("<!-- <section_7_bottom_section_image2> -->", xx) and 'src="' in extract_data("<!-- <section_7_bottom_section_image2> -->", xx) else None,
                            "alt_text": extract_data("<!-- <section_7_bottom_section_image2> -->", xx).split('alt="')[-1].split('"')[0] if extract_data("<!-- <section_7_bottom_section_image2> -->", xx) and 'alt="' in extract_data("<!-- <section_7_bottom_section_image2> -->", xx) else None,
                            "category": extract_data("<!-- <section_7_bottom_section_category2> -->", xx)
                        },
                        "post_3": {
                            "title": extract_data("<!-- <section_7_bottom_section_title3> -->", xx),
                            "date": extract_data("<!-- <section_7_bottom_section_date3> -->", xx),
                            "publisher": extract_data("<!-- <section_7_bottom_section_publisher3> -->", xx),
                            "image": extract_data("<!-- <section_7_bottom_section_image3> -->", xx).split('src="')[-1].split('"')[0] if extract_data("<!-- <section_7_bottom_section_image3> -->", xx) and 'src="' in extract_data("<!-- <section_7_bottom_section_image3> -->", xx) else None,
                            "alt_text": extract_data("<!-- <section_7_bottom_section_image3> -->", xx).split('alt="')[-1].split('"')[0] if extract_data("<!-- <section_7_bottom_section_image3> -->", xx) and 'alt="' in extract_data("<!-- <section_7_bottom_section_image3> -->", xx) else None,
                            "category": extract_data("<!-- <section_7_bottom_section_category3> -->", xx)
                        },
                        "post_4": {
                            "title": extract_data("<!-- <section_7_bottom_section_title4> -->", xx),
                            "date": extract_data("<!-- <section_7_bottom_section_date4> -->", xx),
                            "publisher": extract_data("<!-- <section_7_bottom_section_publisher4> -->", xx),
                            "image": extract_data("<!-- <section_7_bottom_section_image4> -->", xx).split('src="')[-1].split('"')[0] if extract_data("<!-- <section_7_bottom_section_image4> -->", xx) and 'src="' in extract_data("<!-- <section_7_bottom_section_image4> -->", xx) else None,
                            "alt_text": extract_data("<!-- <section_7_bottom_section_image4> -->", xx).split('alt="')[-1].split('"')[0] if extract_data("<!-- <section_7_bottom_section_image4> -->", xx) and 'alt="' in extract_data("<!-- <section_7_bottom_section_image4> -->", xx) else None,
                            "category": extract_data("<!-- <section_7_bottom_section_category4> -->", xx)
                        }
                    }
                },
            }
        }
    }
    return home_page_data




def update_homepage(
        section_1_title: str = None,
        section_1_date: str = None,
        section_1_publisher: str = None,
        section_1_image: str = None,

        section_1_top_right_section_title1: str = None,
        section_1_top_right_section_date1: str = None,
        section_1_top_right_section_publisher1: str = None,
        section_1_top_right_image1: str = None,

        section_1_top_right_section_title2: str = None,
        section_1_top_right_section_date2: str = None,
        section_1_top_right_section_publisher2: str = None,
        section_1_top_right_image2: str = None,

        section_1_left_bottom_section_title: str = None,
        section_1_left_bottom_section_date: str = None,
        section_1_left_bottom_section_publisher: str = None,
        section_1_left_bottom_image: str = None,

        section_2_title: str = None,
        section_2_date: str = None,
        section_2_publisher: str = None,
        section_2_image: str = None,

        section_3_title: str = None,
        section_3_description: str = None,

        section_4_title: str = None,
        section_4_date: str = None,
        section_4_publisher: str = None,
        section_4_image: str = None,

        section_5_header: str = None,
        section_5_title: str = None,
        section_5_date: str = None,
        section_5_publisher: str = None,
        section_5_image: str = None,
        section_5_alt_text: str = None,
        section_5_time: str = None,
        section_5_category: str = None,

        section_5_left_section_title1: str = None,
        section_5_left_section_date1: str = None,
        section_5_left_section_publisher1: str = None,
        section_5_left_section_image1: str = None,
        section_5_left_section_alt_text1: str = None,
        section_5_left_section_category1: str = None,

        section_5_left_section_title2: str = None,
        section_5_left_section_date2: str = None,
        section_5_left_section_publisher2: str = None,
        section_5_left_section_image2: str = None,
        section_5_left_section_alt_text2: str = None,
        section_5_left_section_category2: str = None,

        section_5_bottom_section_title1: str = None,
        section_5_bottom_section_date1: str = None,
        section_5_bottom_section_publisher1: str = None,
        section_5_bottom_section_image1: str = None,
        section_5_bottom_section_alt_text1: str = None,
        section_5_bottom_section_category1: str = None,

        section_5_bottom_section_title2: str = None,
        section_5_bottom_section_date2: str = None,
        section_5_bottom_section_publisher2: str = None,
        section_5_bottom_section_image2: str = None,
        section_5_bottom_section_alt_text2: str = None,
        section_5_bottom_section_category2: str = None,

        section_5_bottom_section_title3: str = None,
        section_5_bottom_section_date3: str = None,
        section_5_bottom_section_publisher3: str = None,
        section_5_bottom_section_image3: str = None,
        section_5_bottom_section_alt_text3: str = None,
        section_5_bottom_section_category3: str = None,

        section_5_bottom_section_title4: str = None,
        section_5_bottom_section_date4: str = None,
        section_5_bottom_section_publisher4: str = None,
        section_5_bottom_section_image4: str = None,
        section_5_bottom_section_alt_text4: str = None,
        section_5_bottom_section_category4: str = None,

        section_6_image: str = None,

        section_7_header: str = None,
        section_7_title: str = None,
        section_7_date: str = None,
        section_7_publisher: str = None,
        section_7_image: str = None,
        section_7_alt_text: str = None,
        section_7_time: str = None,
        section_7_category: str = None,

        section_7_left_section_title1: str = None,
        section_7_left_section_date1: str = None,
        section_7_left_section_publisher1: str = None,
        section_7_left_section_image1: str = None,
        section_7_left_section_alt_text1: str = None,
        section_7_left_section_category1: str = None,

        section_7_left_section_title2: str = None,
        section_7_left_section_date2: str = None,
        section_7_left_section_publisher2: str = None,
        section_7_left_section_image2: str = None,
        section_7_left_section_alt_text2: str = None,
        section_7_left_section_category2: str = None,

        section_7_bottom_section_title1: str = None,
        section_7_bottom_section_date1: str = None,
        section_7_bottom_section_publisher1: str = None,
        section_7_bottom_section_image1: str = None,
        section_7_bottom_section_alt_text1: str = None,
        section_7_bottom_section_category1: str = None,

        section_7_bottom_section_title2: str = None,
        section_7_bottom_section_date2: str = None,
        section_7_bottom_section_publisher2: str = None,
        section_7_bottom_section_image2: str = None,
        section_7_bottom_section_alt_text2: str = None,
        section_7_bottom_section_category2: str = None,

        section_7_bottom_section_title3: str = None,
        section_7_bottom_section_date3: str = None,
        section_7_bottom_section_publisher3: str = None,
        section_7_bottom_section_image3: str = None,
        section_7_bottom_section_alt_text3: str = None,
        section_7_bottom_section_category3: str = None,

        section_7_bottom_section_title4: str = None,
        section_7_bottom_section_date4: str = None,
        section_7_bottom_section_publisher4: str = None,
        section_7_bottom_section_image4: str = None,
        section_7_bottom_section_alt_text4: str = None,
        section_7_bottom_section_category4: str = None
):
    
    # Get the path to the homepage.html file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, '..', '..', 'templates', 'homepage.html')
    
    # Read the current content of the file
    with open(file_path, encoding="utf8") as f:
        content = f.read()
    
    # Function to update text content between markers
    def update_content(marker, new_value):
        nonlocal content
        if new_value is not None:
            escaped_marker = re.escape(marker)
            pattern = f"{escaped_marker}(.*?){escaped_marker}"
            content = re.sub(pattern, f"{marker}{new_value}{marker}", content, count=1, flags=re.DOTALL)
    
    # Function to update background images
    def update_bg_image(marker, new_image):
        nonlocal content
        if new_image is not None:
            update_content(marker, f"bg-[url({new_image})]")
    
    # Function to update image src and/or alt attributes while preserving class
    def update_image_attributes(marker, new_src=None, new_alt=None):
        nonlocal content
        if new_src is None and new_alt is None:
            return  # Nothing to update
            
        escaped_marker = re.escape(marker)
        pattern = f"{escaped_marker}(.*?){escaped_marker}"
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            img_content = match.group(1).strip()
            
            # If new_src is provided, update the src attribute
            if new_src is not None:
                img_content = re.sub(r'src="[^"]*"', f'src="{new_src}"', img_content)
            
            # If new_alt is provided, update the alt attribute
            if new_alt is not None:
                if 'alt="' in img_content:
                    img_content = re.sub(r'alt="[^"]*"', f'alt="{new_alt}"', img_content)
                else:
                    # Add alt attribute if it doesn't exist
                    img_content = img_content.replace('<img ', f'<img alt="{new_alt}" ')
            
            # Update the content while preserving formatting
            content = re.sub(pattern, f"{marker}\n              {img_content}\n              {marker}", content, count=1, flags=re.DOTALL)
    
    # Section 1
    update_content("<!-- <section_1_title> -->", section_1_title)
    update_content("<!-- <section_1_date> -->", section_1_date)
    update_content("<!-- <section_1_publisher> -->", section_1_publisher)
    update_bg_image("<section_1_image>", section_1_image)
    
    # Section 1 Top Right
    update_content("<!-- <section_1_top_right_section_title1> -->", section_1_top_right_section_title1)
    update_content("<!-- <section_1_top_right_section_date1> -->", section_1_top_right_section_date1)
    update_content("<!-- <section_1_top_right_section_publisher1> -->", section_1_top_right_section_publisher1)
    update_bg_image("<section_1_top_right_image1>", section_1_top_right_image1)
    
    update_content("<!-- <section_1_top_right_section_title2> -->", section_1_top_right_section_title2)
    update_content("<!-- <section_1_top_right_section_date2> -->", section_1_top_right_section_date2)
    update_content("<!-- <section_1_top_right_section_publisher2> -->", section_1_top_right_section_publisher2)
    update_bg_image("<section_1_top_right_image2>", section_1_top_right_image2)
    
    # Section 1 Left Bottom
    update_content("<!-- <section_1_left_bottom_section_title1> -->", section_1_left_bottom_section_title)
    update_content("<!-- <section_1_left_bottom_section_date1> -->", section_1_left_bottom_section_date)
    update_content("<!-- <section_1_left_bottom_section_publisher1> -->", section_1_left_bottom_section_publisher)
    update_bg_image("<section_1_left_bottom_image1>", section_1_left_bottom_image)
    
    # Section 2
    update_content("<!-- <section_2_title> -->", section_2_title)
    update_content("<!-- <section_2_date> -->", section_2_date)
    update_content("<!-- <section_2_publisher> -->", section_2_publisher)
    update_bg_image("<section_2_image>", section_2_image)
    
    # Section 3
    update_content("<!-- <section_3_title> -->", section_3_title)
    update_content("<!-- <section_3_description> -->", section_3_description)
    
    # Section 4
    update_content("<!-- <section_4_title> -->", section_4_title)
    update_content("<!-- <section_4_date> -->", section_4_date)
    update_content("<!-- <section_4_publisher> -->", section_4_publisher)
    update_bg_image("<section_4_image>", section_4_image)
    
    # Section 5
    update_content("<!-- <section_5_header> -->", section_5_header)
    update_content("<!-- <section_5_title> -->", section_5_title)
    update_content("<!-- <section_5_date> -->", section_5_date)
    update_content("<!-- <section_5_publisher> -->", section_5_publisher)
    update_content("<!-- <section_5_time> -->", section_5_time)
    update_content("<!-- <section_5_category> -->", section_5_category)
    
    # For sections 5 and 7, update image tags with src and/or alt attributes
    update_image_attributes("<!-- <section_5_image> -->", section_5_image, section_5_alt_text)
    
    # Section 5 Left Section
    update_content("<!-- <section_5_left_section_title1> -->", section_5_left_section_title1)
    update_content("<!-- <section_5_left_section_date1> -->", section_5_left_section_date1)
    update_content("<!-- <section_5_left_section_publisher1> -->", section_5_left_section_publisher1)
    update_content("<!-- <section_5_left_section_category1> -->", section_5_left_section_category1)
    update_image_attributes("<!-- <section_5_left_section_image1> -->", section_5_left_section_image1, section_5_left_section_alt_text1)
    
    # Continue with similar updates for other sections
    update_content("<!-- <section_5_left_section_title2> -->", section_5_left_section_title2)
    update_content("<!-- <section_5_left_section_date2> -->", section_5_left_section_date2)
    update_content("<!-- <section_5_left_section_publisher2> -->", section_5_left_section_publisher2)
    update_content("<!-- <section_5_left_section_category2> -->", section_5_left_section_category2)
    update_image_attributes("<!-- <section_5_left_section_image2> -->", section_5_left_section_image2, section_5_left_section_alt_text2)
    
    # Section 5 Bottom Section
    update_content("<!-- <section_5_bottom_section_title1> -->", section_5_bottom_section_title1)
    update_content("<!-- <section_5_bottom_section_date1> -->", section_5_bottom_section_date1)
    update_content("<!-- <section_5_bottom_section_publisher1> -->", section_5_bottom_section_publisher1)
    update_content("<!-- <section_5_bottom_section_category1> -->", section_5_bottom_section_category1)
    update_image_attributes("<!-- <section_5_bottom_section_image1> -->", section_5_bottom_section_image1, section_5_bottom_section_alt_text1)
    
    # Add all remaining sections...
    update_content("<!-- <section_5_bottom_section_title2> -->", section_5_bottom_section_title2)
    update_content("<!-- <section_5_bottom_section_date2> -->", section_5_bottom_section_date2)
    update_content("<!-- <section_5_bottom_section_publisher2> -->", section_5_bottom_section_publisher2)
    update_content("<!-- <section_5_bottom_section_category2> -->", section_5_bottom_section_category2)
    update_image_attributes("<!-- <section_5_bottom_section_image2> -->", section_5_bottom_section_image2, section_5_bottom_section_alt_text2)
    
    update_content("<!-- <section_5_bottom_section_title3> -->", section_5_bottom_section_title3)
    update_content("<!-- <section_5_bottom_section_date3> -->", section_5_bottom_section_date3)
    update_content("<!-- <section_5_bottom_section_publisher3> -->", section_5_bottom_section_publisher3)
    update_content("<!-- <section_5_bottom_section_category3> -->", section_5_bottom_section_category3)
    update_image_attributes("<!-- <section_5_bottom_section_image3> -->", section_5_bottom_section_image3, section_5_bottom_section_alt_text3)
    
    update_content("<!-- <section_5_bottom_section_title4> -->", section_5_bottom_section_title4)
    update_content("<!-- <section_5_bottom_section_date4> -->", section_5_bottom_section_date4)
    update_content("<!-- <section_5_bottom_section_publisher4> -->", section_5_bottom_section_publisher4)
    update_content("<!-- <section_5_bottom_section_category4> -->", section_5_bottom_section_category4)
    update_image_attributes("<!-- <section_5_bottom_section_image4> -->", section_5_bottom_section_image4, section_5_bottom_section_alt_text4)
    
    # Section 6
    update_bg_image("<section_6_image>", section_6_image)
    
    # Section 7
    update_content("<!-- <section_7_header> -->", section_7_header)
    update_content("<!-- <section_7_title> -->", section_7_title)
    update_content("<!-- <section_7_date> -->", section_7_date)
    update_content("<!-- <section_7_publisher> -->", section_7_publisher)
    update_content("<!-- <section_7_time> -->", section_7_time)
    update_content("<!-- <section_7_category> -->", section_7_category)
    update_image_attributes("<!-- <section_7_image> -->", section_7_image, section_7_alt_text)
    
    # Section 7 Left Section
    update_content("<!-- <section_7_left_section_title1> -->", section_7_left_section_title1)
    update_content("<!-- <section_7_left_section_date1> -->", section_7_left_section_date1)
    update_content("<!-- <section_7_left_section_publisher1> -->", section_7_left_section_publisher1)
    update_content("<!-- <section_7_left_section_category1> -->", section_7_left_section_category1)
    update_image_attributes("<!-- <section_7_left_section_image1> -->", section_7_left_section_image1, section_7_left_section_alt_text1)
    
    update_content("<!-- <section_7_left_section_title2> -->", section_7_left_section_title2)
    update_content("<!-- <section_7_left_section_date2> -->", section_7_left_section_date2)
    update_content("<!-- <section_7_left_section_publisher2> -->", section_7_left_section_publisher2)
    update_content("<!-- <section_7_left_section_category2> -->", section_7_left_section_category2)
    update_image_attributes("<!-- <section_7_left_section_image2> -->", section_7_left_section_image2, section_7_left_section_alt_text2)
    
    # Section 7 Bottom Section
    update_content("<!-- <section_7_bottom_section_title1> -->", section_7_bottom_section_title1)
    update_content("<!-- <section_7_bottom_section_date1> -->", section_7_bottom_section_date1)
    update_content("<!-- <section_7_bottom_section_publisher1> -->", section_7_bottom_section_publisher1)
    update_content("<!-- <section_7_bottom_section_category1> -->", section_7_bottom_section_category1)
    update_image_attributes("<!-- <section_7_bottom_section_image1> -->", section_7_bottom_section_image1, section_7_bottom_section_alt_text1)
    
    update_content("<!-- <section_7_bottom_section_title2> -->", section_7_bottom_section_title2)
    update_content("<!-- <section_7_bottom_section_date2> -->", section_7_bottom_section_date2)
    update_content("<!-- <section_7_bottom_section_publisher2> -->", section_7_bottom_section_publisher2)
    update_content("<!-- <section_7_bottom_section_category2> -->", section_7_bottom_section_category2)
    update_image_attributes("<!-- <section_7_bottom_section_image2> -->", section_7_bottom_section_image2, section_7_bottom_section_alt_text2)
    
    update_content("<!-- <section_7_bottom_section_title3> -->", section_7_bottom_section_title3)
    update_content("<!-- <section_7_bottom_section_date3> -->", section_7_bottom_section_date3)
    update_content("<!-- <section_7_bottom_section_publisher3> -->", section_7_bottom_section_publisher3)
    update_content("<!-- <section_7_bottom_section_category3> -->", section_7_bottom_section_category3)
    update_image_attributes("<!-- <section_7_bottom_section_image3> -->", section_7_bottom_section_image3, section_7_bottom_section_alt_text3)
    
    update_content("<!-- <section_7_bottom_section_title4> -->", section_7_bottom_section_title4)
    update_content("<!-- <section_7_bottom_section_date4> -->", section_7_bottom_section_date4)
    update_content("<!-- <section_7_bottom_section_publisher4> -->", section_7_bottom_section_publisher4)
    update_content("<!-- <section_7_bottom_section_category4> -->", section_7_bottom_section_category4)
    update_image_attributes("<!-- <section_7_bottom_section_image4> -->", section_7_bottom_section_image4, section_7_bottom_section_alt_text4)
    
    # Write the updated content back to the file
    with open(file_path, 'w', encoding="utf8") as f:
        f.write(content)
    
    return "Homepage updated successfully!"

def generate_html_from_json(json_data, indent_level=0):
    html_output = []
    indent_space = "&nbsp;" * 4 * indent_level

    if isinstance(json_data, dict):
        for key, value in json_data.items():
            html_output.append(f"{indent_space}<div><strong>{key}:</strong></div>")
            html_output.append(generate_html_from_json(value, indent_level + 1))
    elif isinstance(json_data, list):
        for item in json_data:
            html_output.append(f"{indent_space}<div>-</div>")
            html_output.append(generate_html_from_json(item, indent_level + 1))
    else:
        html_output.append(f"{indent_space}<p>{json_data}</p>")

    return "\n".join(html_output)