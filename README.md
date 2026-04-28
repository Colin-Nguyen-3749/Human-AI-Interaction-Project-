# Human-AI-Interaction-Project-
This is the group final project for CAS4127, where we aim to build a chatbot to help spread news literacy. 

# ReRoot

## Technic Titans
### Mandy Chen, Colin Nguyen, Seulbit Park

### Introduction

Keeping up with the news can be overwhelming for some as there’s so much to keep track of and complicated information. Names, events, and important contextual information can be daunting when one is trying to understand the world that’s around them, especially when there’s so many sources out there. It can be difficult to consolidate everything into something more concise, yet it’s important that we stay up to date on current events around the world. 

Being informed can not only encourage us to take action or to drive change, but it can also be helpful on a less grandiose (but still very important) scale. It’s important for us to know why certain changes are happening in the world and how they may affect us and the ones around us. For example, one might wonder why the prices of certain products may be climbing higher, or why there’s a new policy that didn’t exist before. It’s especially important for young people, the next generation of leaders, to stay informed about current events as it is the world that we will be inheriting from older generations.

Our team has researched how AI can help us with this task. Often, people only read the headline, leading to easy acceptance of what the media says. Our goal is as follows: to concisely summarize the news so that it can be tolerated by the easily distracted, to break down complicated ideas and jargon, and to provide context that the media does not disclose. 

### Related Work

Based on research conducted in 2025, AI has potential in digital governance and public services, voter outreach, as well as civic engagement (5). One example regarding civic engagement was a platform called Pol.is, which tracks public opinion. As of August 2018, “the website claims it had been used in 26 cases, with 80 percent leading to decisive government action (6).” This is interesting because we see large language models enhancing understanding and AI becoming an empowering tool for civic engagement. 

Another case is recent: a Pennsylvania startup using AI to promote civic action. This case is quite similar to our team’s idea as the founders used OpenAI’s API to “show users a plain-language summary of a bill and explain how it could affect them through related news articles…users can then generate a personalized message — complete with a call to action — and send it to each of their elected representatives (3).” 

However, where our project diverges is that our tool will be tailored to work with any news source, and it will have the added benefit of offering to analyze the bias and credibility of the source at hand in addition to a digestible summary of current events. This way people will still be able to engage with news in a time efficient way while offering an informative perspective. This is our attempt at encouraging users to put more thought into the news that they read, rather than just quickly assuming that everything they read must be the truth and that everything else must be false. It helps people develop a sense of nuance and open-mindedness, rather than just permanently being stuck in their own perspective. Rather than requiring users to visit a separate platform, our project is focused on developing a tool that works like slow technology: integrating an AI tool into environments of consumption similar to a browser extension.

### Motivation & Target

One inspiration of this project came from the idea of stakeholder participation: “all the ways in which citizens and stakeholders can be involved in the policy cycle and in service design and delivery (2).”  With the prevalence of information around us, the main goal our team aims to achieve with this project is thus to promote media literacy, trust, and user empowerment through human centered AI design. Rather than having users navigate the news world in black and white (truth versus propaganda), we hope users can explore evidence by themselves and form conclusions with their own agency. 

For instance, in 2024 there was news claiming North Korea was providing canned dog meat (7). Many people took it as real news without questioning its authenticity due to political bias. Some people argued that due to linguistic differences (the differences in how South and North Koreans call dog meat), the report may have been fabricated or misleading. This example underlines the importance of the statement that it is“ imperative to mitigate AI’s harms and leverage its benefits for democracy could not come at a more critical time (4).” Rather than being an extension of political systems, we can consider AI as a way to critically evaluate information rather than passively accepting it. 

Since we aim for our system to bridge the knowledge gap and also cultural understanding, we hope users can be guided towards more thoughtful actions such as learning from verified and non-bias sources, contacting representatives, and more. This project has potential in exploring how AI can move beyond just generating information and delivering it to the user, instead, becoming a civic partner that educates and encourages more engaged global citizens. 



### Outline of Approach
#### System
Currently, we envision our project to be a small AI tool appearing at the corner of a user’s window when they enter an online news source. It then analyzes the news article and outputs a quick, concise summary of the article, saving the user’s time of reading each detail. We hope to also output a list of biases that exist in the article. This would be possible by training our AI with multiple news datasets to identify misinformation and political or ethnic biases. After the user is presented with a concise and short summary of important topics, they have an option to look for more information or clarification in case of confusion. 

Then, using an AI API, we will create Javascript code that will allow us to connect to the AI API and customize the chatbot. We plan to utilize the Google Chrome web extension to deploy our AI. Since this website would strictly be just for the purposes of reporting and summarizing news, explicit guardrails will be written into our AI chatbot to ensure that it will consistently stay on topic. 

We are considering deploying a Cloudflare worker in order to protect our API key so that there is no risk of someone else mishandling our API. Once we have our chatbot embedded into our website, we will delve into the customization of the chatbot and thorough, consistent testing of the chatbot’s functions. 

#### User Study
For our user study, we’d like to test out our website with a number of students to then follow up with a survey. Our target group would include both those who feel like they are adequately caught up on recent world news and those who do not. Using a simple Google form, we’d give the users a few days to a week to try out the chatbot so that they can have enough time to formulate their opinions on it. Then, we would survey them with questions like:

- Did you feel that the news summary was presented in an objective, unbiased way? If not, why?
- How often do you think you would use this chatbot?
- Does this AI chatbot provide significant convenience?
- How accurate do you think the information provided is?
- Does the usage of this program increase or decrease your trust in AI?
- Was the output appropriate? Was it too long, short, vague, or esoteric (niche, too specific)?
- Do you think that this chatbot increased your awareness of world events, or your interest in them?
- Do you think that there are any ethical concerns about this chatbot?

These questions will be designed so that users can mark a simple answer option (like yes/no, Likert scale values, etc) with the ability to explain their answer in a short-answer format. That way, we can gain both quantitative and qualitative data.

Finally, we’d generate a report with summary statistics with key takeaways to present to the class, including a demonstration of how the chatbot works and our findings in the user study.




### Milestones

- [x] April 15-21: Finish proposal & create Google form to gather feedback
- [x] April 21-24: Adjust proposal and/or Google form as needed 
- [ ] April 27-May 8: Start chatbot/AI extension tool
- [ ] May 11-15: Finish a working prototype of the chatbot
- [ ] May 15-29: Conduct user study & adjust as needed
- [ ] June 1-5: Create presentation
- [ ] June 9th - Present project 



### Specialities and Roles

While everyone will share the responsibility of coding and user testing, each member brings strengths and experience that allow them to lead specific aspects of the project. 

Colin has prior experience in coding AI Chatbots, positioning him to lead the team in tasks involving backend development, user testing, and iterative test development. His expertise will allow us to improve functionality after user studies. 

Seulbit has experience in frontend/backend development and user interface, having worked with React.js and Vercel. Her prior experience will aid in components involving web application as well as teaching the rest of the team how to use these tools. 

Mandy specializes in AI ethics, global technology, and has a little bit of experience in SQL as well as webscraping. This will provide the team with a perspective regarding responsible AI implementation as well as consider how international politics, policy, and regional contexts can shape technology development/adoption. 

While each member may have their own speciality, there will be cross collaboration in all aspects of the project. 



### Expected Challenges

The first challenge we expect to face is making sure that our AI tool is without bias. As our main goal is to inform users and promote active civil participation, instead of catering to the user’s needs, we aim to provide unbiased information, leaving the user to independently form their own opinions. However, to successfully do this, we would have to train the model with a dataset that is free from political bias. It requires us to find reliable news outlets that provide unbiased information, which is quite difficult to find and measure in today’s day and age.

Secondly, due to limited time and our lack of expertise, our team faces the challenge of implementing a properly trained, fine-tuned AI tool within a month. We may get the basics down but whether it can be effectively used by actual users in their day-to-day life is a concern. This leads to the question of if we manage to develop our AI tool as a web extension whether companies would be willing to adopt our technology for their users.

Lastly, we expect to face the challenge of incentivizing our user. Users are already used to passive consumption, so our AI may have to include an emotional or human incentive to achieve our goal of going beyond information consumption. Even when the user does take actions for change our tool provides, it may just be surface level involvement. There is a crucial need to train our model to provide effective and relevant suggestions to prevent turning civic action into performative participation.



### Project Success Definition

In the worst case scenario, our AI tool will only end up being a chatbot that has a limited selection of topics and gives a basic summary of one news article. Furthermore, it also may not provide a robust bias analysis. This is assuming that we are unable to train the model with more datasets. Also, in the worst scenario, we run out of time so we cannot train the model to make suggestions for the user to take action according to certain information.

Average success is having multiple sources of news articles make up a summary for the user’s desired topic or highlights of the day’s news. Although it may not be incredibly life-changing, the AI tool will suggest one to two non-personalized ways for the user to initiate change related to the articles.

In the best possible scenario, the AI tool will provide detailed summaries of any topic the user desires without any political biases. It will suggest personalized, relevant ways for the user to contribute to their local community.



### LLM Usage 

While ChatGPT was not directly used in writing the proposal, we did use Grammarly’s LLM to double check spelling and grammar for this proposal. Also, Co-Pilot helped look for synonyms to certain words for less redundancy. 



### Works Cited
https://www.oecd.org/en/publications/governing-with-artificial-intelligence_795de142-en/full-report/ai-in-civic-participation-and-open-government_51227ce7.html 
https://www.publicsource.org/ai-tech-democracy-pittsburgh-lawmakers/ 
https://carnegieendowment.org/research/2026/01/ai-and-democracy-mapping-the-intersections 

https://www.nationalcivicleague.org/ncr-article/digitized-democracy-how-ai-is-reshaping-governance-and-civic-life/ 
https://www.technologyreview.com/2018/08/21/240284/the-simple-but-ingenious-system-taiwan-uses-to-crowdsource-its-laws/ 
https://vifreepress.com/2024/11/russian-frontline-soldiers-reduced-to-eating-canned-dog-meat-from-north-korea/ 

