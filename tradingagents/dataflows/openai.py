import os
from openai import OpenAI
from .config import get_config

# Import Gemini if available
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


def _get_response_with_search(prompt, config, search_config=None):
    """
    Get a response from either OpenAI or Gemini based on config.
    
    Args:
        prompt: The prompt to send to the LLM
        config: Configuration dictionary with llm_provider and model settings
        search_config: Optional dict with search configuration:
            - search_context_size: "low", "medium", or "high" (default: "low")
            - user_location: "approximate" or "precise" (default: "approximate")
        
    Returns:
        str: The response text from the LLM
    """
    llm_provider = config.get("llm_provider", "openai").lower()
    
    # Default search configuration
    if search_config is None:
        search_config = {
            "search_context_size": "low",
            "user_location": "approximate",
        }
    
    if llm_provider == "google":
        print("Using Google/Gemini with Google Search")
        if not GEMINI_AVAILABLE:
            raise ImportError(
                "google-generativeai package is not installed. "
                "Install it with: pip install google-generativeai"
            )
        
        # Configure Gemini
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY environment variable is not set. "
                "Please set it to use Gemini provider."
            )
        
        genai.configure(api_key=api_key)
        
        # Perform Google Search using googlesearch-python library
        # This provides real search results to enhance the Gemini response
        try:
            from googlesearch import search
            
            # Extract key search terms from prompt (use first 100 chars)
            search_query = prompt[:100] if len(prompt) > 100 else prompt
            
            # Perform Google search (top 5 results)
            search_results = []
            try:
                print(f"[DEBUG]-_get_response_with_search- Searching Google for: {search_query[:50]}...")
                for url in search(search_query, num_results=5):
                    search_results.append(f"- {url}")
                    
                print(f"[DEBUG]-_get_response_with_search- Found {len(search_results)} search results")
            except Exception as search_error:
                print(f"[WARNING] Google search failed: {search_error}")
            
            # Enhance prompt with search results
            if search_results:
                enhanced_prompt = (
                    f"{prompt}\n\n"
                    f"Here are relevant search results from Google:\n"
                    + "\n".join(search_results) + "\n\n"
                    f"Please provide a comprehensive answer based on the above information."
                )
            else:
                enhanced_prompt = prompt
                
        except ImportError:
            print("[WARNING] googlesearch-python not installed. Using prompt without search enhancement.")
            enhanced_prompt = prompt
        
        # Create model without search grounding (SDK limitation)
        model = genai.GenerativeModel(
            model_name=config["quick_think_llm"]
        )
        
        print(f"[DEBUG]-_get_response_with_search- Model: {config['quick_think_llm']}")
        print(f"[DEBUG]-_get_response_with_search- Enhanced Prompt:\n{enhanced_prompt[:200]}...")
        
        # Generate response
        response = model.generate_content(
            enhanced_prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.1,
                top_p=1.0,
                max_output_tokens=4096,
            )
        )

        print(f"[DEBUG]-_get_response_with_search- Response generated successfully")
        
        return response.text
    
    else:  # Default to OpenAI
        print("Using OpenAI")
        client = OpenAI(base_url=config["backend_url"])
        
        # Use search_config for OpenAI web search
        search_context_size = search_config.get("search_context_size", "low")
        user_location_type = search_config.get("user_location", "approximate")
        
        response = client.responses.create(
            model=config["quick_think_llm"],
            input=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": prompt,
                        }
                    ],
                }
            ],
            text={"format": {"type": "text"}},
            reasoning={},
            tools=[
                {
                    "type": "web_search_preview",
                    "user_location": {"type": user_location_type},
                    "search_context_size": search_context_size,
                }
            ],
            temperature=1,
            max_output_tokens=4096,
            top_p=1,
            store=True,
        )
        
        return response.output[1].content[0].text


def get_stock_news_openai(query, start_date, end_date):
    """
    Retrieve stock news using either OpenAI or Gemini.
    
    Args:
        query: Stock ticker or company name
        start_date: Start date in yyyy-mm-dd format
        end_date: End date in yyyy-mm-dd format
        
    Returns:
        str: News articles about the stock
    """
    config = get_config()
    prompt = (
        f"Can you search Social Media for {query} from {start_date} to {end_date}? "
        f"Make sure you only get the data posted during that period."
    )
    return _get_response_with_search(prompt, config)


def get_global_news_openai(curr_date, look_back_days=7, limit=5):
    """
    Retrieve global news using either OpenAI or Gemini.
    
    Args:
        curr_date: Current date in yyyy-mm-dd format
        look_back_days: Number of days to look back (default 7)
        limit: Maximum number of articles to return (default 5)
        
    Returns:
        str: Global news articles
    """
    config = get_config()
    prompt = (
        f"Can you search global or macroeconomics news from {look_back_days} days before {curr_date} "
        f"to {curr_date} that would be informative for trading purposes? "
        f"Make sure you only get the data posted during that period. "
        f"Limit the results to {limit} articles."
    )
    return _get_response_with_search(prompt, config)


def get_fundamentals_openai(ticker, curr_date):
    """
    Retrieve fundamental data using either OpenAI or Gemini.
    
    Args:
        ticker: Stock ticker symbol
        curr_date: Current date in yyyy-mm-dd format
        
    Returns:
        str: Fundamental data table
    """
    config = get_config()
    prompt = (
        f"Can you search Fundamental for discussions on {ticker} during of the month before {curr_date} "
        f"to the month of {curr_date}. Make sure you only get the data posted during that period. "
        f"List as a table, with PE/PS/Cash flow/ etc"
    )
    return _get_response_with_search(prompt, config)