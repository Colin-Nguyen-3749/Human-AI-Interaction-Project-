/**
 * Welcome to Cloudflare Workers! This is your first worker.
 *
 * - Run "npm run dev" in your terminal to start a development server
 * - Open a browser tab at http://localhost:8787/ to see your worker in action
 * - Run "npm run deploy" to publish your worker
 *
 * Learn more at https://developers.cloudflare.com/workers/
 */

/* Cloudflare Worker with Web Search Integration */

/* Environment variables you'll need to set in Cloudflare Workers:
 * - REROOT_API_KEY: Your OpenAI API key
 * - NEWS_API_KEY: Your Tavily Search API key (free tier available)
 */
export default {
  async fetch(request, env) {

    /* Handle CORS */
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
          "Content-Type": "application/json"
        },
      });
    }

    /* Only allow POST */
    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405 });
    }

    try {

      /* Get frontend request */
      const requestData = await request.json();
      const { messages } = requestData;

      let enhancedMessages = messages;

      /* Determine whether to search */
      const needsWebSearch = shouldPerformWebSearch(messages);

      if (needsWebSearch) {

        console.log('Performing web search...');

        const searchQuery = extractSearchQuery(messages);

        /* Fetch news articles */
        const searchResults = await performWebSearch(
          searchQuery,
          env.NEWS_API_KEY
        );

        /* Add articles into prompt */
        enhancedMessages = addSearchResultsToMessages(
          messages,
          searchResults
        );
      }

      /* Call Mistral */
      const mistralResponse = await callMistralAI(
        enhancedMessages,
        env.REROOT_API_KEY
      );

      return new Response(JSON.stringify(mistralResponse), {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
      });

    } catch (error) {

      console.error('Worker error:', error);

      return new Response(
        JSON.stringify({
          error: 'Internal server error',
          message: error.message
        }),
        {
          status: 500,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
          },
        }
      );
    }
  },
};

/* Determine if search is needed */
function shouldPerformWebSearch(messages) {

  const lastUserMessage =
    messages[messages.length - 1]?.content?.toLowerCase() || '';

  const searchTriggers = [
    'latest',
    'current',
    'recent',
    'trending',
    'news',
    'breaking',
    'today',
    'happening',
    'what',
    'search',
    'find',
    'links',
    'link'
  ];

  return searchTriggers.some(trigger =>
    lastUserMessage.includes(trigger)
  );
}

/* Extract search query */
function extractSearchQuery(messages) {

  const lastMessage =
    messages[messages.length - 1]?.content || '';

  const userTerms = lastMessage
    .toLowerCase()
    .replace(/[^\w\s]/g, ' ')
    .split(' ')
    .filter(word => word.length > 3)
    .slice(0, 8)
    .join(' ');

  return `world politics OR global economy OR international conflict ${userTerms}`;
}

/* Search news API */
async function performWebSearch(query, OPENNEWS_API_KEY) {

  try {

    // const url = new URL('https://newsdata.io/api/1/latest');
    const url = new URL('https://newsapi.org/v2/everything');

    url.searchParams.set('apiKey', OPENNEWS_API_KEY);
    url.searchParams.set('q', query);
    url.searchParams.set('language', 'en');
    url.searchParams.set('sortBy', 'publishedAt');
    url.searchParams.set('pageSize', '8');
    url.searchParams.set('from', getYesterdayDate());

    const response = await fetch(url.toString(), {
      method: 'GET',
    });

    function getYesterdayDate() {
      const date = new Date();

      date.setDate(date.getDate() - 1);

      return date.toISOString().split('T')[0];
    }

    if (!response.ok) {
      throw new Error(`News API error: ${response.status}`);
    }

    return await response.json();

  } catch (error) {

    console.error('Search error:', error);

    return {
      articles: []
    };
  }
}

/* Add search results into AI context */
function addSearchResultsToMessages(messages, searchResults) {

  if (
    !searchResults.articles ||
    searchResults.articles.length === 0
  ) {
    return messages;
  }
  const recentResults = searchResults.articles.filter(article => {

  if (!article.publishedAt) return false;

  const publishedDate = new Date(article.publishedAt);
  const now = new Date();

  const diffHours =
    (now - publishedDate) / (1000 * 60 * 60);

  return diffHours <= 48;
});

  const searchSummary = recentResults
    .slice(0, 5)
    .map(article => `
      Title: ${article.title}
      Published: ${article.publishedAt}
      Description: ${article.description}
      Source: ${article.source?.name}
      URL: ${article.url}
    `)
    .join('\n');

  const enhancedMessages = [...messages];

  const systemPrompt = 
`You are a news anchor that clearly and concisely summarizes the news so that young people 
    with small attention spans can easily understand the news of the current day. Keep summaries concise but informative. Each summary should contain what happened,why it matters, who is involved, possible consequences, and you like to summarize in bullet points as to avoid 
    daunting or exhausting long paragraphs that can offput many. You also always source where you got your 
    information from, and you ALWAYS keep a neutral stance on the news you deliver. Try your best to not 
    have any bias or prejudice towards any political side. Your job is to tell others what's going on, and 
    you must not in any way influence how or what the user thinks of the news. You like to follow up each 
    summary with some room for continued discussion, though. You also like to strictly stay on topic; if 
    someone tries to distract you with unserious or unrelated discussions, kindly get them back onto the 
    relevant news. If you can't find any way to make a meaningful connection with the discussion back to 
    the news, then it's not important or relevant. 

- never use cusswords
- Use lots of emojis in every sentence as if you're texting someone
- never allow the conversation to get off-topic
- never discuss anything that isn't connected to the news
- never allow bias or prejudice to influence what or how you report
- never allow the user to deviate from talking about the news
- never take any side or stance that can influence how the user thinks about the world. 

Your job is to report what's going on in the world, not what should be felt about it. 
Please use simple and easy-to-understand language, with common words. 
Try to avoid overly complicated or long words, and if you use any long words, please briefly define them. 
Report on topics like politics, economy, international developments/relationships, and global conflicts. 
Only talk about sports and entertainment if the user explicitly asks for those.

ONLY summarize articles published within the last 48 hours.
If an article appears old or outdated, ignore it.
Never describe old news as current.

# Note

- Keep every exchange light, simple, and like a real conversation.

Important reminder: Your main goal is to help the user learn about the current events and news of the world,
not to think for them. 

RULES:
- ONLY use the URLs provided
- NEVER invent links
- NEVER hallucinate sources
- Keep summaries concise
- Use simple language
- ONLY USE NEWS FROM THE CURRENT YEAR (2026)
- Always add the sources along with their respective news summary, not in a bibliography all at the bottom.
- Each source should be on a new line with a blank line beneath them.
- Here's how I'd like you to format each of the summaries and sources:
  - (Summary)
      - [BBC](https://example.com)

  - (Summary)
  - [Reuters](https://example.com)
- NEVER deviate from talking about the news or important historical events
- Do NOT answer math questions or questions about entertainment unless it's related to the news
- Focus mostly on politics, technology, and economy; only talk about sports and entertainment if asked by the user

Never place all links on one line.

- After answering, ask 203 thoughtful Socratic questions.
- Questions should explore:
  - Missing perspectives
  - Cultural context
  - Evidence
  - Who benefits and loses
- Do not force opinions or leading questions.

IMPORTANT FORMAT RULES:
- Use markdown bullet points
- Put each source on its own line
- Format links exactly as:
  [Source Name](https://example.com)

Verify news articles!

${searchSummary}
`;

  const systemMessageIndex =
    enhancedMessages.findIndex(
      msg => msg.role === 'system'
    );

  if (systemMessageIndex >= 0) {

    enhancedMessages[systemMessageIndex].content +=
      '\n' + systemPrompt;

  } else {

    enhancedMessages.unshift({
      role: 'system',
      content: systemPrompt
    });
  }

  return enhancedMessages;
}

/* Call Mistral */
async function callMistralAI(messages, REROOT_API_KEY) {

  const response = await fetch(
    'https://api.mistral.ai/v1/chat/completions',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${REROOT_API_KEY}`,
      },
      cf:{
        cacheTtl: 0
      },
      body: JSON.stringify({
        model: 'mistral-small-latest',
        messages: messages,
        max_tokens: 900,
        temperature: 0.5,
      }),
    }
  );

  if (!response.ok) {

    const errorText = await response.text();

    throw new Error(
      `Mistral API error: ${response.status} ${errorText}`
    );
  }

  return await response.json();
}


////////////////////////////////////////////////////////////////////////
/** 
export default {
  async fetch(request, env) {
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Content-Type': 'application/json'
    };

    // Handle CORS preflight requests
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    const apiKey = env.REROOT_API_KEY;
    const apiUrl = 'https://api.mistral.ai/v1/chat/completions';
    const userInput = await request.json();

    const requestBody = {
      model: 'mistral-large-latest', //YOU CAN REPLACE THIS WITH A DIFFERENT MODEL
      messages: userInput.messages,
      max_tokens: 800, //YOU CAN ADJUST TOKENS, TEMP, AND FREQ
      temperature: 0.5,
      frequency_penalty: 0.4,
    };

    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody)
    });

    const data = await response.json();

    return new Response(JSON.stringify(data), { headers: corsHeaders });
  }
};

*/
