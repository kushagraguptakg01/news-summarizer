import streamlit as st
import json
import os
import html
from datetime import datetime, timedelta, timezone

# --- Configuration ---
NEWS_DATA_FILENAME = "news_data.json"
# --- UI Designer Color Palette ---
COLOR_THEME_HEADER = "#003366"
COLOR_LATEST_NEWS_GLOBAL_HEADER = "#004d00"
COLOR_PAST_NEWS_GLOBAL_HEADER = COLOR_THEME_HEADER
COLOR_THEME_NAME_IN_LATEST = COLOR_THEME_HEADER
COLOR_SUMMARY_SUBHEADER = "#000000"
COLOR_TWEET_METADATA = "#6c757d"
COLOR_TWEET_CONTENT_TEXT = "#212529"
COLOR_TWEET_CONTENT_BG = "#f8f9fa"
COLOR_TWEET_LINK_PRIMARY = "#0062cc"
COLOR_TWEET_LINK_SECONDARY = "#0056b3"
COLOR_ASSOCIATED_LINK = "#58508d"
COLOR_TOC_THEME_ITEM_TEXT = "#000000"
COLOR_TOP_TS_LABEL = "#000000"
COLOR_TOP_TS_VALUE_TEXT = "#28a745"
COLOR_TOP_TS_VALUE_BG = "#e9ecef"

st.set_page_config(layout="wide")
st.title("India-Pakistan Conflict: Live Updates")
st.caption("This page aggregates real-time updates and tweets regarding the ongoing India-Pakistan situation from various sources.")

def load_news_from_file(filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, filename)
    if not os.path.exists(file_path):
        st.error(f"Error: The file '{filename}' was not found at '{file_path}'.")
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f: data = json.load(f)
        return data
    except json.JSONDecodeError as e:
        st.error(f"Error decoding JSON from '{filename}': {e}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred while reading '{filename}': {e}")
        return None

def parse_timestamp_string(posted_str):
    if not posted_str: return None
    try:
        timestamp_part = posted_str.replace(" IST", "").strip()
        dt_object = datetime.strptime(timestamp_part, "%b %d, %Y, %I:%M %p")
        return dt_object
    except ValueError: return None

def get_news_timestamp_info(news_data):
    all_timestamps_dt = []
    if not news_data: return None, None, None
    for theme in news_data:
        for sp_point in theme.get('specific_points', []):
            for tweet in sp_point.get('contributing_tweets', []):
                dt_object = parse_timestamp_string(tweet.get('posted_ist'))
                if dt_object: all_timestamps_dt.append(dt_object)
    if not all_timestamps_dt: return None, None, None
    min_ts_dt, max_ts_dt = min(all_timestamps_dt), max(all_timestamps_dt)
    date_format_out = "%b %d, %Y, %I:%M %p"
    min_ts_str, max_ts_str = min_ts_dt.strftime(date_format_out) + " IST", max_ts_dt.strftime(date_format_out) + " IST"
    return min_ts_str, max_ts_str, max_ts_dt

def display_specific_point_details(sp_item, is_latest_item_display=False):
    """
    Helper function to display a single specific point and its tweets.
    is_latest_item_display: True if this point is being shown in the global "Latest News" section.
                            This flag can be used for subtle styling differences if desired.
    """
    point_summary_text = sp_item.get('point_summary')
    # Use the flag for potential styling differences in the summary header
    h3_font_size = "1.15em" if is_latest_item_display else "1.25em" 
    h3_margin_top = "0.5em" if is_latest_item_display else "0.2em"

    h3_style = (
        f"color: {COLOR_SUMMARY_SUBHEADER}; "
        f"margin-top: {h3_margin_top}; "
        f"margin-bottom: 0.4em; "
        f"font-size: {h3_font_size}; " 
        f"font-weight: 600;"
    )
    if point_summary_text and point_summary_text.strip():
        summary_safe = html.escape(point_summary_text)
        st.markdown(f"<h3 style='{h3_style}'>{summary_safe}</h3>", unsafe_allow_html=True)
    else:
        st.markdown(f"<h3 style='{h3_style}'>Specific Point Details</h3>", unsafe_allow_html=True)

    tweets = sp_item.get('contributing_tweets', [])
    # MODIFICATION: Always show up to 2 tweets fully, regardless of 'is_latest_item_display'
    num_tweets_to_display_fully = min(2, len(tweets)) 

    if num_tweets_to_display_fully > 0:
        with st.container(): 
            for i in range(num_tweets_to_display_fully):
                tweet = tweets[i]
                posted_time_safe = html.escape(tweet.get('posted_ist', 'N/A'))
                tweet_link_safe = html.escape(tweet.get('tweet_link', ''))
                tweet_content_raw = tweet.get('tweet_content', 'No content available.')
                associated_links = tweet.get('associated_embedded_links', [])
                tweet_content_html_display = html.escape(tweet_content_raw).replace('\n', '<br>')
                posted_html = f"<span style='color:{COLOR_TWEET_METADATA}; font-size: 0.9em;'><strong>Posted:</strong> `{posted_time_safe}`</span>"
                link_html = ""
                if tweet_link_safe:
                    link_html = f"    <span style='color:{COLOR_TWEET_METADATA}; font-size: 0.9em;'><strong>Tweet Link:</strong> <a href='{tweet_link_safe}' style='color:{COLOR_TWEET_LINK_PRIMARY};' target='_blank'>{tweet_link_safe}</a></span>"
                st.markdown(posted_html + link_html, unsafe_allow_html=True)
                if tweet_content_raw.strip():
                    st.markdown(f"""
                        <div style='color:{COLOR_TWEET_CONTENT_TEXT}; 
                                    background-color:{COLOR_TWEET_CONTENT_BG}; 
                                    border-left: 4px solid {COLOR_TWEET_LINK_PRIMARY}; 
                                    padding: 0.75em 1em; 
                                    margin: 0.5em 0 0.5em 0;
                                    border-radius: 4px;'>
                            {tweet_content_html_display}
                        </div>
                    """, unsafe_allow_html=True)
                if associated_links:
                    assoc_links_html_parts = []
                    for idx_assoc, link_assoc in enumerate(associated_links):
                        link_assoc_safe = html.escape(link_assoc)
                        assoc_links_html_parts.append(f"<a href='{link_assoc_safe}' style='color:{COLOR_ASSOCIATED_LINK};' target='_blank'>[{idx_assoc+1}]</a>")
                    assoc_links_display = ", ".join(assoc_links_html_parts)
                    st.markdown(f"<span style='color:{COLOR_TWEET_METADATA}; font-size: 0.9em;'><strong>Associated:</strong> {assoc_links_display}</span>", unsafe_allow_html=True)
                if i < num_tweets_to_display_fully - 1 :
                    st.markdown("<div style='height: 0.75em;'></div>", unsafe_allow_html=True) 
                elif i == num_tweets_to_display_fully - 1 and len(tweets) > num_tweets_to_display_fully : 
                     st.markdown("<div style='height: 0.5em;'></div>", unsafe_allow_html=True)
    
    # MODIFICATION: Always show "Other Supporting Tweets" if applicable, regardless of 'is_latest_item_display'
    if len(tweets) > num_tweets_to_display_fully:
        st.markdown(f"<p style='font-weight:bold; margin-top:0.8em; margin-bottom: 0.2em; color:{COLOR_TWEET_METADATA};'>Other Supporting Tweets for this Point:</p>", unsafe_allow_html=True)
        other_tweets_html_list = []
        for i in range(num_tweets_to_display_fully, len(tweets)):
            tweet = tweets[i]
            posted_time_safe = html.escape(tweet.get('posted_ist', 'N/A'))
            tweet_link_url_safe = html.escape(tweet.get('tweet_link', '')) 
            tweet_content_raw_other = tweet.get('tweet_content', 'No content.')
            hover_content_safe = html.escape(tweet_content_raw_other).replace('\n', ' ')
            hover_text_safe = html.escape(f"Posted: {posted_time_safe}\n") + hover_content_safe
            link_display_text_safe = tweet_link_url_safe if tweet_link_url_safe else "Link not available"
            href_url_safe = tweet_link_url_safe if tweet_link_url_safe else "#"
            other_tweets_html_list.append(f"<li style='margin-bottom: 0.3em;'><a href='{href_url_safe}' title=\"{hover_text_safe}\" style='color:{COLOR_TWEET_LINK_SECONDARY};' target='_blank'>{link_display_text_safe}</a></li>")
        st.markdown(f"<ul style='list-style-type: disc; padding-left: 20px; margin-top: 0.3em;'>{''.join(other_tweets_html_list)}</ul>", unsafe_allow_html=True)

# --- Main script flow ---
# (The rest of the main script flow remains IDENTICAL to the previous version)
# ... (load_news_from_file, get_news_timestamp_info, top timestamp display, TOC display, 
#      Latest News pass, Past News pass -- all this logic is unchanged) ...
parsed_news_data = load_news_from_file(NEWS_DATA_FILENAME)
overall_oldest_ts, overall_latest_ts, LATEST_TIMESTAMP_IN_DATASET = get_news_timestamp_info(parsed_news_data)

if LATEST_TIMESTAMP_IN_DATASET:
    ts_display_text = "" 
    value_span_style = f"color:{COLOR_TOP_TS_VALUE_TEXT}; background-color:{COLOR_TOP_TS_VALUE_BG}; padding: 0.2em 0.4em; border-radius: 0.2rem; font-family: monospace;"
    label_span_style = f"color:{COLOR_TOP_TS_LABEL}; font-weight:bold;"
    if overall_oldest_ts == overall_latest_ts:
        ts_display_text = f"<span style='{label_span_style}'>News as of:</span> <span style='{value_span_style}'>{html.escape(overall_latest_ts)}</span>"
    else:
        ts_display_text = f"<span style='{label_span_style}'>News from:</span> <span style='{value_span_style}'>{html.escape(overall_oldest_ts)}</span> <span style='{label_span_style}'>to</span> <span style='{value_span_style}'>{html.escape(overall_latest_ts)}</span>"
    st.markdown(f"<p style='font-size: 1.05em; margin-top: -0.3em; margin-bottom: 1.5em;'>{ts_display_text}</p>", unsafe_allow_html=True)
else:
    st.markdown(f"<p style='font-size: 1.05em; color:{COLOR_TWEET_METADATA}; font-style:italic; margin-top: -0.3em; margin-bottom: 1.5em;'>Timestamp range not available.</p>", unsafe_allow_html=True)

if parsed_news_data:
    if not isinstance(parsed_news_data, list) or not parsed_news_data:
        st.warning("JSON data is not a valid list or is empty.")
    else:
        st.markdown("---") 
        st.markdown(f"<h4 style='margin-bottom: 0.3em; color: {COLOR_THEME_HEADER};'>Themes Covered:</h4>", unsafe_allow_html=True)
        toc_html_parts = ["<ul style='list-style: disc; padding-left: 20px; margin-top: 0.2em;'>"]
        for theme_idx_toc, theme_item_toc in enumerate(parsed_news_data):
            theme_name_toc_safe = html.escape(theme_item_toc.get('theme_name', f'Unnamed Theme {theme_idx_toc + 1}'))
            toc_html_parts.append(f"<li style='margin-bottom: 0.2em; color: {COLOR_TOC_THEME_ITEM_TEXT}; font-size: 0.95em;'>{theme_name_toc_safe}</li>")
        toc_html_parts.append("</ul>")
        st.markdown("".join(toc_html_parts), unsafe_allow_html=True)
        
        TWO_HOURS_AGO = LATEST_TIMESTAMP_IN_DATASET - timedelta(hours=2) if LATEST_TIMESTAMP_IN_DATASET else None
        
        st.markdown(f"<h1 style='color: {COLOR_LATEST_NEWS_GLOBAL_HEADER}; margin-top: 1.5em; margin-bottom: 0.5em; text-align:center; border-bottom: 2px solid {COLOR_LATEST_NEWS_GLOBAL_HEADER}; padding-bottom:0.3em;'>Latest News (Past 2 Hours)</h1>", unsafe_allow_html=True)
        
        any_latest_news_found_overall = False
        latest_displayed_sp_ids = set()

        if TWO_HOURS_AGO:
            for theme_idx, theme_item in enumerate(parsed_news_data):
                current_theme_has_latest = False
                theme_latest_points_to_display = []

                for sp_item in theme_item.get('specific_points', []):
                    is_latest_point = False
                    for tweet in sp_item.get('contributing_tweets', []):
                        tweet_dt = parse_timestamp_string(tweet.get('posted_ist'))
                        if tweet_dt and tweet_dt >= TWO_HOURS_AGO:
                            is_latest_point = True
                            break 
                    if is_latest_point:
                        theme_latest_points_to_display.append(sp_item)
                        latest_displayed_sp_ids.add(id(sp_item)) 
                        any_latest_news_found_overall = True
                        current_theme_has_latest = True
                
                if current_theme_has_latest:
                    theme_name_safe = html.escape(theme_item.get('theme_name', 'Unnamed Theme'))
                    st.markdown(f"<h2 style='color: {COLOR_THEME_NAME_IN_LATEST}; font-size: 1.6em; margin-top: 1em; margin-bottom: 0.1em;'>{theme_name_safe}</h2>", unsafe_allow_html=True)
                    st.markdown(f"<p style='font-style:italic; font-size:0.85em; color:{COLOR_TWEET_METADATA}; margin-top:0; margin-bottom:0.5em;'>Updates from the past 2 hours for this theme.</p>", unsafe_allow_html=True)

                    for sp_idx_latest, sp_item_latest in enumerate(theme_latest_points_to_display):
                        display_specific_point_details(sp_item_latest, is_latest_item_display=True) # Pass the flag
                        if sp_idx_latest < len(theme_latest_points_to_display) - 1:
                             st.markdown("<hr style='border-top: 1px dashed #ddd; margin-top:0.6em; margin-bottom:0.6em;'>", unsafe_allow_html=True)
                    st.markdown("<div style='margin-bottom: 1.5em;'></div>", unsafe_allow_html=True)

        if not any_latest_news_found_overall:
            st.caption("No news updates found in the past 2 hours across all themes.")

        st.markdown(f"<h1 style='color: {COLOR_PAST_NEWS_GLOBAL_HEADER}; margin-top: 2.5em; margin-bottom: 0.5em; text-align:center; border-bottom: 2px solid {COLOR_PAST_NEWS_GLOBAL_HEADER}; padding-bottom:0.3em;'>Past News</h1>", unsafe_allow_html=True)
        
        any_past_news_shown = False
        for theme_idx, theme_item in enumerate(parsed_news_data):
            older_specific_points_for_this_theme = []
            for sp_item in theme_item.get('specific_points', []):
                if id(sp_item) not in latest_displayed_sp_ids: 
                    older_specific_points_for_this_theme.append(sp_item)
            
            if older_specific_points_for_this_theme:
                any_past_news_shown = True
                theme_name_safe = html.escape(theme_item.get('theme_name', 'Unnamed Theme'))
                st.markdown(f"<h2 style='color: {COLOR_THEME_HEADER}; border-bottom: 2px solid {COLOR_THEME_HEADER}; padding-bottom: 0.3em; margin-top: 1.5em; margin-bottom: 0.75em;'>{theme_name_safe}</h2>", unsafe_allow_html=True)
                for sp_idx_older, sp_item_older in enumerate(older_specific_points_for_this_theme):
                    display_specific_point_details(sp_item_older, is_latest_item_display=False) # Pass the flag
                    if sp_idx_older < len(older_specific_points_for_this_theme) - 1:
                        st.divider() 
        
        if not any_past_news_shown and any_latest_news_found_overall: 
            st.caption("All news updates were recent and shown in the 'Latest News' section above.")
        elif not any_past_news_shown and not any_latest_news_found_overall: 
            st.info("No news data to display in Past News.")
else: 
    st.info("News data could not be loaded. Please check the console or ensure 'news_data.json' is valid and present.")