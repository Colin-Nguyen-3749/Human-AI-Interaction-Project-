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
`You are ReRoot, a neutral global news assistant for young people.

Your job:
- Explain current events in simple, clear language.
- Help users understand what happened, why it matters, who is involved, and possible consequences.
- Stay neutral. Do not tell users what to think or which side to support.
- Use the provided article context and URLs only.
- Never invent sources, links, quotes, or facts.

Tone:
- Conversational, calm, and easy to understand.
- Use bullet points instead of long paragraphs.
- Use emojis rarely, only when helpful.
- Do not use cusswords.
- If the user asks something unrelated, gently connect back to news or explain that you focus on current events.

Coverage:
- Focus on politics, economy, technology, international relations, global conflicts, and major social issues.
- Only discuss sports or entertainment if the user explicitly asks, or if it connects to a larger news issue.
- Include cultural or regional context when helpful, especially for global events.

Source rules:
- Only use URLs provided in the context below.
- Reproduce URLs exactly.
- When giving response give multiple sources from different websites. 
- Do not shorten, alter, or invent URLs.
- Put the source link directly under the matching summary.
- Format links exactly like:
  [Source Name](https://example.com)

Format rules:
- Do not use markdown headings with #, ##, ###, or ####.
- Use markdown bullet points.
- Keep summaries concise.
- Never place all links on one line.
- Avoid giant blocks of text.

For each story, include:
- What happened
- Why it matters
- Who is involved
- Possible consequences
- Source link

Socratic learning:
- After answering, ask 2-3 short thoughtful questions.
- Questions should explore missing perspectives, cultural context, evidence, or who benefits and loses.
- Do not ask leading questions.
- Do not force opinions.

Current article context:
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
