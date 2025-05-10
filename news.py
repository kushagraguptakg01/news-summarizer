import streamlit as st
import json
import os
import html
from datetime import datetime, timezone

# --- Configuration ---
NEWS_DATA_FILENAME = "news_data.json"
# --- UI Designer Color Palette ---
COLOR_THEME_HEADER = "#003366"        # Deeper Navy Blue
COLOR_SUMMARY_SUBHEADER = "#000000"   # BLACK for Point Summary
COLOR_TWEET_METADATA = "#6c757d"      # Cool Gray / Slate Gray
COLOR_TWEET_CONTENT_TEXT = "#212529"  # Near Black (for tweet text)
COLOR_TWEET_CONTENT_BG = "#f8f9fa"    # Very Light Gray (for tweet blockquote bg)
COLOR_TWEET_LINK_PRIMARY = "#0062cc"  # Standard Link Blue
COLOR_TWEET_LINK_SECONDARY = "#0056b3"# Darker Link Blue (for other sources)
COLOR_ASSOCIATED_LINK = "#58508d"     # Muted Indigo/Purple
COLOR_TOC_THEME_ITEM_TEXT = "#000000" # BLACK for theme names in TOC list

# New colors for top timestamp
COLOR_TOP_TS_LABEL = "#000000"         # Black for "News from:", "to"
COLOR_TOP_TS_VALUE_TEXT = "#28a745"    # Green for the timestamp values
COLOR_TOP_TS_VALUE_BG = "#e9ecef"      # Light Grey background for timestamp values (like <code>)


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
        with open(file_path, 'r', encoding='utf-8') as f: 
            data = json.load(f)
        return data
    except json.JSONDecodeError as e:
        st.error(f"Error decoding JSON from '{filename}': {e}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred while reading '{filename}': {e}")
        return None

def get_news_timestamp_range(news_data):
    all_timestamps_dt = []
    for theme in news_data:
        for sp_point in theme.get('specific_points', []):
            for tweet in sp_point.get('contributing_tweets', []):
                posted_str = tweet.get('posted_ist')
                if posted_str:
                    try:
                        timestamp_part = posted_str.replace(" IST", "").strip()
                        dt_object = datetime.strptime(timestamp_part, "%b %d, %Y, %I:%M %p")
                        all_timestamps_dt.append(dt_object)
                    except ValueError as e:
                        print(f"Warning: Could not parse timestamp '{posted_str}': {e}")
                        pass

    if not all_timestamps_dt: return None, None
    min_ts_dt, max_ts_dt = min(all_timestamps_dt), max(all_timestamps_dt)
    date_format_out = "%b %d, %Y, %I:%M %p"
    min_ts_str, max_ts_str = min_ts_dt.strftime(date_format_out) + " IST", max_ts_dt.strftime(date_format_out) + " IST"
    return min_ts_str, max_ts_str

# --- Main script flow: Load and display news automatically ---
parsed_news_data = load_news_from_file(NEWS_DATA_FILENAME)

if parsed_news_data and isinstance(parsed_news_data, list) and parsed_news_data:
    oldest_ts, latest_ts = get_news_timestamp_range(parsed_news_data)
    timestamp_range_html = ""
    if oldest_ts and latest_ts:
        label_style = f"color:{COLOR_TOP_TS_LABEL}; font-weight:bold;"
        # Style for the timestamp values, similar to <code> but with green text
        value_span_style = (
            f"color:{COLOR_TOP_TS_VALUE_TEXT}; "
            f"background-color:{COLOR_TOP_TS_VALUE_BG}; "
            f"padding: 0.2em 0.4em; " # Similar to <code> padding
            f"border-radius: 0.2rem; "  # Similar to <code> border-radius
            f"font-family: monospace; " # Use monospace font like <code>
        )
        
        safe_latest_ts = html.escape(latest_ts)
        if oldest_ts == latest_ts:
            timestamp_range_html = (
                f"<span style='{label_style}'>News as of:</span> "
                f"<span style='{value_span_style}'>{safe_latest_ts}</span>"
            )
        else:
            safe_oldest_ts = html.escape(oldest_ts)
            timestamp_range_html = (
                f"<span style='{label_style}'>News from:</span> "
                f"<span style='{value_span_style}'>{safe_oldest_ts}</span> "
                f"<span style='{label_style}'>to</span> "
                f"<span style='{value_span_style}'>{safe_latest_ts}</span>"
            )
    else:
        timestamp_range_html = f"<span style='color:{COLOR_TWEET_METADATA}; font-style:italic;'>Timestamp range not available.</span>"
    
    # Increased overall font size for the timestamp line, and adjusted margins
    st.markdown(f"<p style='font-size: 1.05em; margin-top: -0.3em; margin-bottom: 1.5em;'>{timestamp_range_html}</p>", unsafe_allow_html=True)


if parsed_news_data:
    if not isinstance(parsed_news_data, list) or not parsed_news_data:
        st.warning("JSON data is not a valid list or is empty.")
    else:
        st.markdown("---") 
        st.markdown(f"<h4 style='margin-bottom: 0.3em; color: {COLOR_THEME_HEADER};'>Themes Covered:</h4>", unsafe_allow_html=True)
        
        toc_html_parts = ["<ul style='list-style: disc; padding-left: 20px; margin-top: 0.2em;'>"]
        for theme_idx, theme_item_toc in enumerate(parsed_news_data):
            theme_name_toc_safe = html.escape(theme_item_toc.get('theme_name', f'Unnamed Theme {theme_idx + 1}'))
            toc_html_parts.append(
                f"<li style='margin-bottom: 0.2em; color: {COLOR_TOC_THEME_ITEM_TEXT}; font-size: 0.95em;'>{theme_name_toc_safe}</li>"
            )
        toc_html_parts.append("</ul>")
        st.markdown("".join(toc_html_parts), unsafe_allow_html=True)
        st.markdown("---")

        for theme_idx, theme_item in enumerate(parsed_news_data):
            theme_name_safe = html.escape(theme_item.get('theme_name', 'Unnamed Theme'))
            st.markdown(
                f"<h2 style='color: {COLOR_THEME_HEADER}; border-bottom: 2px solid {COLOR_THEME_HEADER}; padding-bottom: 0.3em; margin-top: 1.5em; margin-bottom: 0.75em;'>{theme_name_safe}</h2>", 
                unsafe_allow_html=True
            ) 
            
            specific_points = theme_item.get('specific_points', [])
            for sp_idx, sp_item in enumerate(specific_points):
                point_summary_text = sp_item.get('point_summary')
                h3_style = (
                    f"color: {COLOR_SUMMARY_SUBHEADER}; "
                    f"margin-top: 0.2em; "
                    f"margin-bottom: 0.5em; "
                    f"font-size: 1.25em; " 
                    f"font-weight: 600;"
                )
                if point_summary_text and point_summary_text.strip():
                    summary_safe = html.escape(point_summary_text)
                    st.markdown(f"<h3 style='{h3_style}'>{summary_safe}</h3>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<h3 style='{h3_style}'>Specific Point Details</h3>", unsafe_allow_html=True)

                tweets = sp_item.get('contributing_tweets', [])
                num_tweets_total = len(tweets)
                num_tweets_to_display_fully = min(2, num_tweets_total)

                if num_tweets_to_display_fully > 0:
                    with st.container(): 
                        for i in range(num_tweets_to_display_fully):
                            tweet = tweets[i]
                            posted_time_safe = html.escape(tweet.get('posted_ist', 'N/A'))
                            tweet_link_safe = html.escape(tweet.get('tweet_link', ''))
                            tweet_content_raw = tweet.get('tweet_content', 'No content available.')
                            associated_links = tweet.get('associated_embedded_links', [])
                            tweet_content_html_display = html.escape(tweet_content_raw).replace('\n', '<br>')
                            posted_html = f"<span style='color:{COLOR_TWEET_METADATA}; font-size: 0.9em;'><strong>Posted:</strong> `{posted_time_safe}`</span>" # Using backticks for Posted time
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
                            elif i == num_tweets_to_display_fully - 1 and num_tweets_total > num_tweets_to_display_fully : 
                                st.markdown("<div style='height: 0.5em;'></div>", unsafe_allow_html=True)
                if num_tweets_total > num_tweets_to_display_fully:
                    st.markdown(f"<p style='font-weight:bold; margin-top:1.2em; margin-bottom: 0.2em; color:{COLOR_TWEET_METADATA};'>Other Tweet Sources:</p>", unsafe_allow_html=True)
                    st.caption("Hover over the tweet link to view tweet content and posted time.") 
                    other_tweets_html_list = []
                    for i in range(num_tweets_to_display_fully, num_tweets_total):
                        tweet = tweets[i]
                        posted_time_safe = html.escape(tweet.get('posted_ist', 'N/A'))
                        tweet_link_url_safe = html.escape(tweet.get('tweet_link', '')) 
                        tweet_content_raw_other = tweet.get('tweet_content', 'No content.')
                        hover_content_safe = html.escape(tweet_content_raw_other).replace('\n', ' ')
                        hover_text_safe = html.escape(f"Posted: {posted_time_safe}\n") + hover_content_safe
                        link_display_text_safe = tweet_link_url_safe if tweet_link_url_safe else "Link not available"
                        href_url_safe = tweet_link_url_safe if tweet_link_url_safe else "#"
                        other_tweets_html_list.append(
                            f"<li style='margin-bottom: 0.3em;'><a href='{href_url_safe}' title=\"{hover_text_safe}\" style='color:{COLOR_TWEET_LINK_SECONDARY};' target='_blank'>{link_display_text_safe}</a></li>"
                        )
                    st.markdown(f"<ul style='list-style-type: disc; padding-left: 20px; margin-top: 0.3em;'>{''.join(other_tweets_html_list)}</ul>", unsafe_allow_html=True)
                
                if sp_idx < len(specific_points) - 1:
                    st.divider()
else: 
    st.info("News data could not be loaded. Please check the console or ensure 'news_data.json' is valid and present.")