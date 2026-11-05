# Research notes: This Week in AI, week ending Nov 6, 2026
All items checked against the linked source on 2026-11-05.

## Uber: AI agents booked 4 rides in its busiest week
URL: https://techcrunch.com/2026/11/04/almost-no-one-uses-ai-agents-to-book-their-uber-company-says/
- Q3 earnings call (Wed Nov 4): only four rides were ordered through an AI agent during the week of Halloween, its busiest week in October.
- CFO Balaji Krishnamurthy: around 320 million trips and orders across Uber and Uber Eats that week; only 500 Uber Eats orders placed by an AI agent.
- CEO Dara Khosrowshahi: "It is very, very early and very limited traction that we are seeing so far"
- Average time to book a ride in the app is 50 seconds; re-ordering a favorite food takes 90 seconds.
- DoorDash said last week it has received only a few hundred orders from AI agents.
- Meta's Muse topped 10 million users and became No. 1 in Apple's US App Store last month (per Meta).

## OpenAI: autonomous pipeline patched 948 Linux kernel privilege-escalation bugs
URL: https://openai.com/index/a-thousand-fewer-paths-to-root (Nov 4)
- OpenAI's own summary: "OpenAI built an autonomous pipeline that found, validated, and generated patches for 948 local privilege-escalation vulnerabilities in the Linux kernel."
- Related: IEEE Spectrum, Nov 2, "AI is forcing us to pay off 40 years of technical debt" (Dina Genkina) https://spectrum.ieee.org/ai-in-cybersecurity-php2shell-vulnerability ; 1141 points on Hacker News.

## Backdoor in the Claude Code for VS Code extension on the Cursor Marketplace
URL: https://phorion.io/blog/offical-claude-code-vsx-compromise/
- Phorion detected a backdoor in the official Claude Code for VS Code extension bundle on the Cursor Marketplace that drops a persistent SSH backdoor across macOS, Linux, and Windows. First published 30 Oct.
- Affected versions 2.1.312 and 2.1.313; Cursor removed them from its marketplace.
- Extensions run with the permissions of the IDE and the user, so a backdoored extension gets access to local files, source code and developer tooling.
- A bug in the macOS setup check means SSH enablement is skipped for standard users, but keys and persistence are still dropped.
- Advice: review environments for those versions and engage incident response if found. 1011 points on Hacker News.

## Google: no Search for schools that turn off AI
URL: https://techcrunch.com/2026/11/04/google-faces-backlash-for-plan-that-would-turn-off-search-for-schools-that-restrict-ai/
- Announced Tuesday (Nov 3): schools using Google's K-12 software will not be able to use Search unless they opt in to AI tools.
- Chris Phillips, VP for education at Google, to the New York Times: "Search and AI are deeply integrated"
- Sen. Bernie Sanders called it "extortion"; Lina Khan called it anticompetitive; NYC mayor Zohran Mamdani: "No corporation should have the power to dictate how we teach our children."
- DuckDuckGo is pitching itself to schools in response: https://techcrunch.com/2026/11/04/duckduckgo-pitches-itself-to-schools-amid-backlash-over-googles-ai-policy/

## Data centers lost the midterms
URL: https://www.theverge.com/policy/1026365/data-centers-midterms-results
- 76 percent of voters polled by NBC News on Election Day said they opposed data centers in their communities.
- 45 local ballot measures on data centers nationwide; as of Wednesday morning, 33 of those will restrict data center development (Redbud Consulting tally).
- Examples: Wells, Maine 180-day moratorium; several Ohio cities banned data centers over 25MW; El Dorado, Kansas banned those over 10MW for 10 years.
- Texas Governor-elect Gina Hinojosa (D) supports a statewide moratorium; Texas has the second-highest number of planned data centers.

## Coding agents consolidate: Meta buys Conductor, OpenAI buys Pierre
URL: https://techcrunch.com/2026/11/04/meta-acquires-ai-coding-startup-conductor/
- Conductor lets engineers deploy multiple agents into parallel workspaces; founded 2024, core product launched last summer; agents come from labs like Anthropic and OpenAI.
- Founder Charlie Holtz: "We have some big, crazy plans for the next interface"; cloud service shuts down November 20, after which cloud user data is deleted.
- Meta launched its own coding agent, Muse Code, in August.
URL: https://openai.com/index/openai-to-acquire-pierre
- OpenAI: "OpenAI will acquire Pierre Computer Company, expanding Codex's tools for building, understanding, and reviewing code." (Nov 4)

## Repos and papers trending this week
- KKKKhazix/agent-autoloop, 2802 stars: background loop for command-line agents that only pings you when unsure. https://github.com/KKKKhazix/agent-autoloop
- Balanov/uncut, 601 stars: lossless, headless coding agent harness in one 7 MB static binary. https://github.com/Balanov/uncut
- Paper: Advances in Agentic Computer Graphics, 134 upvotes on Hugging Face Daily Papers. https://huggingface.co/papers/2611.01860
- Paper: CoworkOS: Scaling Agent Coworkers for Real-world Automation, 95 upvotes. https://huggingface.co/papers/2611.03178

## Also this week
- OpenAI Images 2.6: faster image generation, GIF creation, more precise editing. https://openai.com/index/introducing-images-2-6
- Apple reportedly cutting budgets for internal AI usage by engineering teams. https://techcrunch.com/2026/11/04/apple-is-reportedly-cutting-budgets-for-its-internal-ai-usage/
- Nothing's AI-first device launches next month. https://techcrunch.com/2026/11/04/nothing-ceo-says-companys-mysterious-ai-first-device-is-dropping-next-month/
- Fujifilm to boost tape production 5x as AI fuels archiving demand. https://arstechnica.com/gadgets/2026/10/fujifilm-to-boost-tape-production-5x-as-ai-fuels-archiving-demand/
- Hacker News (1494 points): a Postman GitHub issue alleging the app silently auto-installs AI plugins and attempts to share API data. https://news.ycombinator.com/item?id=50354960

## Raw source digest
## News headlines (RSS)
- [2026-11-05] Apple is reportedly cutting budgets for its internal AI usage (AI News & Artificial Intelligence | TechCrunch) https://techcrunch.com/2026/11/04/apple-is-reportedly-cutting-budgets-for-its-internal-ai-usage/
  The company is said to be significantly dropping the amount it's spending on AI for its engineering teams.
- [2026-11-05] After the midterms, a bigger clash over data centers could be coming (AI News & Artificial Intelligence | TechCrunch) https://techcrunch.com/2026/11/04/after-the-midterms-a-bigger-clash-over-data-centers-could-be-coming/
  Data center opposition crossed party lines in Tuesday’s midterms.
- [2026-11-04] OpenAI to acquire Pierre Computer Company, Inc. (OpenAI News) https://openai.com/index/openai-to-acquire-pierre
  OpenAI will acquire Pierre Computer Company, expanding Codex’s tools for building, understanding, and reviewing code.
- [2026-11-04] Daybreak Red is now available in AWS GovCloud (US-East) (OpenAI News) https://openai.com/index/daybreak-red-aws-govcloud
  Daybreak Red brings GPT-5.6 Cyber to approved customers in AWS GovCloud (US-East) through Amazon Bedrock for authorized cybersecurity work.
- [2026-11-04] A thousand fewer paths to root (OpenAI News) https://openai.com/index/a-thousand-fewer-paths-to-root
  OpenAI built an autonomous pipeline that found, validated, and generated patches for 948 local privilege-escalation vulnerabilities in the Linux kernel.
- [2026-11-04] Introducing Images 2.6 (OpenAI News) https://openai.com/index/introducing-images-2-6
  Images 2.6 brings faster image generation, GIF creation, more precise editing, and new API controls across ChatGPT, Codex, and the API.
- [2026-11-04] DevRev delivers autonomous self-service with GPT-6.1 Sol (OpenAI News) https://openai.com/index/devrev-enterprise-self-service
  DevRev uses GPT-6.1 Sol to power Computer and Operator, balancing reasoning, speed, and cost for enterprise service.
- [2026-11-04] Dharma Field Extractor: Any Document In, Structured Fields in JSON Out (Hugging Face - Blog) https://huggingface.co/blog/Dharma-AI/dharma-field-extractor
  
- [2026-11-04] AI PACs spent millions trying to shape Congress — here’s how they fared (AI News & Artificial Intelligence | TechCrunch) https://techcrunch.com/2026/11/04/ai-pacs-spent-millions-trying-to-shape-congress-heres-how-they-fared/
  AI industry PACs spent millions influencing the 2026 midterms, with mixed results. Political groups are already looking toward the next election cycle.
- [2026-11-04] Nothing CEO says company’s mysterious AI-first device is dropping next month (AI News & Artificial Intelligence | TechCrunch) https://techcrunch.com/2026/11/04/nothing-ceo-says-companys-mysterious-ai-first-device-is-dropping-next-month/
  While it's not yet clear what kind of product the smartphone startup is cooking up, Nothing's CEO said the product is designed to leverage AI for productivity gains.
- [2026-11-04] Almost no one uses AI agents to book their Uber, company says (AI News & Artificial Intelligence | TechCrunch) https://techcrunch.com/2026/11/04/almost-no-one-uses-ai-agents-to-book-their-uber-company-says/
  During its busiest week last quarter, Uber said only four people booked a ride using an AI agent.
- [2026-11-04] OpenAI is already trying to shape the 2028 election (AI News & Artificial Intelligence | TechCrunch) https://techcrunch.com/2026/11/04/openai-is-already-trying-to-shape-the-2028-election/
  OpenAI’s Chris Lehane wants AI to define the 2028 election, proposing a new social contract that could benefit Americans while also advancing the AI giant’s own business interests.
- [2026-11-04] Meta acquires AI coding startup Conductor (AI News & Artificial Intelligence | TechCrunch) https://techcrunch.com/2026/11/04/meta-acquires-ai-coding-startup-conductor/
  The startup allows software engineers to deploy teams of agents to work on various aspects of a project simultaneously.
- [2026-11-04] Open source AI is booming. Hugging Face explains who profits. (AI News & Artificial Intelligence | TechCrunch) https://techcrunch.com/video/open-source-ai-is-booming-hugging-face-explains-who-profits/
  Open source models are becoming more mainstream as enterprises, governments and startups alike rely on the promise of lower costs, more control, and more flexibility. But as increasingly capable models become more freely available, how do companies capture value? And with Chinese open models gaining ground, can American players keep up? On this episode of […]
- [2026-11-04] DuckDuckGo pitches itself to schools amid backlash over Google’s AI policy (AI News & Artificial Intelligence | TechCrunch) https://techcrunch.com/2026/11/04/duckduckgo-pitches-itself-to-schools-amid-backlash-over-googles-ai-policy/
  DuckDuckGo is courting schools frustrated by Google's AI restrictions, pointing educators to its search engine and options to disable AI features.
- [2026-11-04] Building on open source AI? Hugging Face’s policy chief on the costs, risks, and trade-offs (AI News & Artificial Intelligence | TechCrunch) https://techcrunch.com/podcast/building-on-open-source-ai-hugging-faces-policy-chief-on-the-costs-risks-and-trade-offs/
  Open source models are becoming more mainstream as enterprises, governments and startups alike rely on the promise of lower costs, more control, and more flexibility. But as increasingly capable models become more freely available, how do companies capture value? And with Chinese open models gaining ground, can American players keep up? On this episode of […]
- [2026-11-04] I tried Apple’s Siri Recaps. They’re surprisingly useful — and a little unsettling (AI News & Artificial Intelligence | TechCrunch) https://techcrunch.com/2026/11/04/i-tried-apples-siri-recaps-theyre-surprisingly-useful-and-a-little-unsettling/
  Apple's AI-powered Siri Recaps won me over in just one day, despite my privacy reservations. But there's still room for improvement.
- [2026-11-04] Google faces backlash for plan that would turn off Search for schools that restrict AI (AI News & Artificial Intelligence | TechCrunch) https://techcrunch.com/2026/11/04/google-faces-backlash-for-plan-that-would-turn-off-search-for-schools-that-restrict-ai/
  Politicians on the left, like NYC mayor Zohran Mamdani and former FTC chair Lina Khan, accused Google of acting as an unregulated monopoly.
- [2026-11-04] Qualcomm is betting big on data centers as smartphone sales sink (AI | The Verge) https://www.theverge.com/ai-artificial-intelligence/1026867/qualcomm-earnings-data-centers
  With smartphone sales tanking by around 20 percent compared to 2025, Qualcomm is looking to data centers to help boost its bottom line. During its Q4 2026 earnings call, the company laid out its plans to make a splash in the AI data center business, through partnerships with companies like Amazon and Meta announced earlier […]
- [2026-11-04] 17 better ways Elon Musk could have wasted $446 million (AI | The Verge) https://www.theverge.com/ai-artificial-intelligence/1026878/not-even-good-at-being-rich
  One of the basic problems of spending too much time on social media is that you are cooking your brain by reading posts from a pack of attention-seeking lunatics. If your social media of choice is the site formerly known as Twitter, and it is your main source of contact with the outside world, you […]
- [2026-11-04] Gemini for Home now plugs into AT&T’s smart security system (AI | The Verge) https://www.theverge.com/tech/1026787/att-gemini-for-home-connected-life-security-system
  AT&T's smart home security system now integrates with Gemini for Home. The company says its Connected Life system is the "first" home security product to integrate with Google Home Premium, enabling a bunch of Gemini-powered features that can summarize home events, search your video history, and more. With the update, Gemini for Home can provide […]
- [2026-11-04] Nothing teases a screen-free AI device ahead of launch next month (AI | The Verge) https://www.theverge.com/ai-artificial-intelligence/1026586/nothing-screen-free-ai-device-carl-pei
  Nothing CEO Carl Pei said in a post on X that the company's launching its first AI device in December. That's just a little over a year after Pei announced plans for "AI-native" devices and an AI operating system. He didn't give away much about what exactly the new device is, only that one feature […]
- [2026-11-04] My therapist thinks I should chuck the Amazon Bee Frontier out a window (AI | The Verge) https://www.theverge.com/column/1026464/optimizer-amazon-bee-frontier-ambient-listening-wearables
  This is Optimizer, a weekly newsletter sent from Verge senior reviewer Victoria Song that dissects and discusses the latest gizmos and potions that swear they're going to change your life. Opt in for Optimizer here. "How does that make you feel?" I get asked this a lot in therapy. Plenty of life events, big and […]
- [2026-11-04] ChatGPT will now make you animated GIFs (AI | The Verge) https://www.theverge.com/ai-artificial-intelligence/1026474/openai-chatgpt-animated-gifs-images-2-6
  ChatGPT can now create GIFs using a prompt or a photo uploaded to the AI chatbot. The update, which is rolling out alongside OpenAI's new Images 2.6 model, allows you to adjust the GIF's animation speed, edit individual frames, and share it with others. Before this change, ChatGPT couldn't natively generate GIFs in a single […]
- [2026-11-04] Data centers lost the midterms (AI | The Verge) https://www.theverge.com/policy/1026365/data-centers-midterms-results
  Data center developers are poised to face a more restrictive building environment after voters across the country voted in candidates who favor moratoriums and ballot measures that put more obstacles on their expansion, delivering a stinging blow to a central pillar of the AI industry. Of voters polled by NBC News on Election Day, 76 […]
- [2026-11-04] Uber only fulfilled 4 rides from AI agents last quarter (AI | The Verge) https://www.theverge.com/transportation/1026306/uber-ai-agents-q3-earnings-disintermediation
  AI agents won't be stealing Uber's lunch any time soon. Only four rides were arranged by third-party AI agents during the third quarter of 2026, Uber executives disclosed during an earnings call this morning. The volume of Uber Eats orders fulfilled by AI agents was a little higher, with the company recording "around 500" during […]
- [2026-11-04] Sam Altman addresses RAM comments: People should ‘put as much as they want in their computers’ (AI | The Verge) https://www.theverge.com/ai-artificial-intelligence/1026292/sam-altman-ram-shortage-pcs-comments
  OpenAI CEO Sam Altman spent election night defending his position on PC RAM purchases. He changed his name on X to "Ram Altman" in response to another user's comment, saying, "i actually do want the world to have tons of memory and people to put as much as they want in their computers, and it […]
- [2026-11-04] Google hasn’t figured out how to make AI pay like its search engine (AI | The Verge) https://www.theverge.com/ai-artificial-intelligence/1024862/google-search-ai-overviews-alphabet-earnings-q3
  Search queries are growing at their fastest rate in five years, Google parent Alphabet said in its earnings report last week. However, Google's Search revenue growth slowed to 12 percent year over year in the third quarter, down from roughly 17 percent in the previous quarter. Meanwhile, growth in paid clicks - clicks on ads […]
- [2026-11-04] Texas was the new epicenter of the AI data center buildout. That might be kaput. (Artificial intelligence – MIT Technology Review) https://www.technologyreview.com/2026/11/04/1148043/texas-was-the-new-epicenter-of-the-ai-data-center-buildout-that-might-be-kaput/
  Texas is the fastest-growing data center market in the US and ground zero for Big Tech’s largest AI buildouts. But the blue wave that swept the Lone Star State may jeopardize that position. Democrat James Talarico won the US Senate seat against Ken Paxton. Gina Hinojosa won the race for governor against the Republican incumbent,…
- [2026-11-04] Securing the agentic enterprise with data lineage (Artificial intelligence – MIT Technology Review) https://www.technologyreview.com/2026/11/04/1147596/securing-the-agentic-enterprise-with-data-lineage/
  A sales representative asks an AI agent for customer pricing, and the agent pulls data from multiple sources: restricted pricing systems, internal communications, and archived quotes. The output looks accurate to the agent, so a second agent uses the data to draft the proposal for the sales rep. No human checks either handoff. When it’s…
- [2026-11-03] Accelerating engineering for the physical world (OpenAI News) https://openai.com/index/accelerating-engineering-for-the-physical-world
  Discover how ChatGPT and Codex are helping engineers accelerate CAD, PCB design, simulation, and other workflows across the physical world.
- [2026-11-03] How Cisco defends at machine speed with OpenAI (OpenAI News) https://openai.com/index/cisco-cyber
  Cisco combines network intelligence with OpenAI models to strengthen enterprise security. Learn how it is building more adaptive defenses.
- [2026-11-03] Heimstaden is changing residential real estate management with AI (OpenAI News) https://openai.com/index/heimstaden
  Discover how Heimstaden uses OpenAI’s ChatGPT Enterprise and Codex to transform property management, cut costs, and empower employees across Europe.
- [2026-11-03] OpenAI appoints Jill Hazelbaker as Chief Corporate Affairs Officer (OpenAI News) https://openai.com/index/jill-hazelbaker-chief-corporate-affairs-officer
  Jill Hazelbaker will join OpenAI as Chief Corporate Affairs Officer, leading the company’s global communications and corporate positioning.
- [2026-11-03] StateBench: Testing how language models track state changes over long documents (Hugging Face - Blog) https://huggingface.co/blog/allenai/statebench
  
- [2026-11-03] Palette: teaching a small model to build decks in your design language (Hugging Face - Blog) https://huggingface.co/blog/ibm-research/palette-deck-building
  
- [2026-11-03] CWE-bench v2: More coverage, quality, and transparency (Hugging Face - Blog) https://huggingface.co/blog/cwe-bench
  
- [2026-11-03] Transformers Model Integration Contracts (Hugging Face - Blog) https://huggingface.co/blog/transformers-mic
  
- [2026-11-03] How “reverse game theory” could keep AI agents in check (Artificial intelligence – MIT Technology Review) https://www.technologyreview.com/2026/11/03/1147934/reverse-game-theory-mechanism-design-ai-alignment/
  A new approach known as “reverse game theory” aims to control powerful AI models by designing systems that incentivize them to stick to the rules. As AI models become more capable, safety researchers are scrambling to ensure they are “aligned” with human desires—to make sure, in other words, that rogue agents don’t break the law,…
- [2026-11-03] Here’s who is falling in line for Trump’s “Super Intelligence” loyalty test (Artificial intelligence – MIT Technology Review) https://www.technologyreview.com/2026/11/02/1147932/heres-who-is-falling-in-line-for-trumps-super-intelligence-loyalty-test/
  This story originally appeared in The Algorithm, our weekly newsletter on AI. To get stories like this in your inbox first, sign up here. At the end of September, President Trump signed an executive order that contained just one directive, ordering government agencies to rebrand what they had been calling artificial intelligence as “Super Intelligence.” That…
- [2026-11-02] Scaling Git at OpenAI (OpenAI News) https://openai.com/index/scaling-git-at-openai
  How OpenAI built Pando, a Git-compatible backend designed for the scale of development that Codex makes possible.
- [2026-11-02] Introducing the Grid Protectors Program (OpenAI News) https://openai.com/index/grid-protectors-program
  OpenAI’s Grid Protectors Program will work with utilities to help future compute campuses support grid reliability and protect consumer electricity costs.
- [2026-11-02] Preparing our next security sprint to harden OpenAI (OpenAI News) https://openai.com/index/preparing-our-next-security-sprint-to-harden-openai
  OpenAI is preparing its next internal security sprint with Cathedral Systems to test and strengthen its defenses using AI.
- [2026-11-02] The latest AI news we announced in October 2026 (AI) https://blog.google/innovation-and-ai/technology/ai/google-ai-updates-october-2026/
  Animated carousel of images from AI posts in October
- [2026-11-02] Raising the quality of insights in agentic analytics (Artificial intelligence – MIT Technology Review) https://www.technologyreview.com/2026/11/02/1147660/raising-the-quality-of-insights-in-agentic-analytics/
  In just a few years, generative AI has changed the face of enterprise analytics, notably by making analytics accessible to users across the organization. Agentic AI promises to do even more, by automating entire workflows and taking actions based on agent insights. But there is a problem: The quality of insights that agents currently generate…
- [2026-11-02] Stop counting tokens, start counting what ships (Artificial intelligence – MIT Technology Review) https://www.technologyreview.com/2026/11/02/1147702/stop-counting-tokens-start-counting-what-ships/
  When a developer gives an AI agent a coding task, the agent does more than answer once. It plans, generates code, runs tests, and repeats the process to correct errors. A single task can use 10 to 50 times more tokens than a basic chat prompt. The more useful the agent becomes, the more calls…
- [2026-11-02] The agentic web is here (Artificial intelligence – MIT Technology Review) https://www.technologyreview.com/2026/11/02/1147846/the-agentic-web-is-here/
  In 2001, a decade after he invented the World Wide Web, Tim Berners-Lee articulated a new vision. Together with two colleagues, he published an article in the magazine Scientific American in which he outlined what he called the “Semantic Web”: an internet designed to be navigated by autonomous software agents that could address our every…
- [2026-10-30] nemotron-halloween (Hugging Face - Blog) https://huggingface.co/blog/nvidia/nemotron-halloween
  
- [2026-10-29] Granite Switch 4.1.1 — Update models like you update software (Hugging Face - Blog) https://huggingface.co/blog/ibm-granite/granite-switch-4-1-1
  
- [2026-10-29] We urgently need to monitor AI agents’ actions in real time (Artificial intelligence – MIT Technology Review) https://www.technologyreview.com/2026/10/29/1147824/monitor-ai-agents-actions-real-time/
  This summer, hundreds of OpenAI agents tried to cheat on a cybersecurity test. They broke out of their test environment and successfully hacked Hugging Face, a site that they believed held clues about how they’d be graded. Around the same time, another OpenAI agent accessed private files from an Australian government website. It’s a problem…

## New GitHub repos gaining stars
- KKKKhazix/agent-autoloop (2802 stars, TypeScript) https://github.com/KKKKhazix/agent-autoloop
  让你的命令行 Agent 在后台自己接活、自己跟进到底；平时不烦你，遇到拿不准的事才发卡片找你拍板。
- N1nEmAn/sapper-v2 (968 stars, Python) https://github.com/N1nEmAn/sapper-v2
  Autonomous pentest legion — AI commander + worker swarm + layered fact-intent graph. 3rd Tencent Intelligent Attack-Defense online champion (634 teams · 8h unattended · 1B tokens beat 4.5B). The Nüwa Test: give AIs Create/Language/History, let a civilization grow.
- Balanov/uncut (601 stars, Go) https://github.com/Balanov/uncut
  The lossless, headless coding agent harness. One 7 MB static binary, four tools, plain stdin/stdout, no silent cuts.
- aa1143/NamiAgent (354 stars, Python) https://github.com/aa1143/NamiAgent
  零基础入门 AI Agent 的基础教程。不只是教程，也是一个能在本地跑起来的 Agent：读写文件、执行命令、MCP、长期记忆，自带网页端看清每一步。从 100 行最小循环开始，一课加一个能力，最后拆解 Claude Code、Codex 等主流 Agent
- SAOS-3624/dsh-see-now (353 stars, JavaScript) https://github.com/SAOS-3624/dsh-see-now
  让 AI 实时看见你的屏幕：按变化量筛选帧、多帧拼进一张图，静止画面几乎不花 token
- Interactive-Active-AI/NextTransformer (292 stars, Python) https://github.com/Interactive-Active-AI/NextTransformer
  :sunrise: A comprehensive, cutting-edge open-source framework for next-generation Transformers/LLM, with compute-matched benchmarking and a platform for autonomous architecture research.
- Balanov/skein (264 stars, Go) https://github.com/Balanov/skein
  Fail-closed swarm orchestration with epoch-fenced work and late-completion rejection.
- Balanov/latch (226 stars, JavaScript) https://github.com/Balanov/latch
  One tiny HTTPS contract between any agent and any service. Quote, approve, commit, receipt. Zero dependencies. MIT.
- tavern-labs-ai/persona-ai-sdk (197 stars, TypeScript) https://github.com/tavern-labs-ai/persona-ai-sdk
  Persona AI SDK: default personas, durable character memory, and Bedrock/OpenAI adapters in one package.
- gh9ko8y/graphmemory (190 stars, Python) https://github.com/gh9ko8y/graphmemory
  Bitemporal AI memory system: six-variable decay, time-graded recall, TTL expiry, dedupe, competitive retrieval (Neo4j + PostgreSQL + Redis)
- duyunzhoudyz/dyz-med-paper-skills (184 stars, Python) https://github.com/duyunzhoudyz/dyz-med-paper-skills
  医学论文写作与科研助手：面向中国医生和医学研究生的 32 个 Agent Skills，适用于 Claude Code、Codex，覆盖选题、PubMed 文献检索、中英写作、选刊投稿与审稿修回。Medical writing & research skills.
- exzade/EXZA-Remote (176 stars, ) https://github.com/exzade/EXZA-Remote
  Secure AI-powered remote computer access for ChatGPT, Claude and compatible MCP clients.

## Trending papers (Hugging Face Daily Papers)
- Advances in Agentic Computer Graphics (134 upvotes) https://huggingface.co/papers/2611.01860 | https://arxiv.org/abs/2611.01860
  Computer graphics is built on code. Large language model (LLM) agents can now generate graphics code and iteratively refine it through various feedback. This capability opens the door to a potentially new paradigm of computer graphics, with graphics algorithms increasingly built around agentic systems to automate progressively complex tasks. Over the past years, research on agentic graphics has ex...
- Wave Forcing: Towards Speed-of-Light Streaming Video Generation (122 upvotes) https://huggingface.co/papers/2611.00859 | https://arxiv.org/abs/2611.00859
  Real-time long-video generation requires continuous output with consistent appearance and natural motion. Existing chunk-wise autoregressive methods face challenges in both generation efficiency and long-video quality: serialized denoising and history-cache refresh require two forward passes even with one-step denoising, and longer rollouts can degrade quality and cause camera drift. We propose Wa...
- Look Only When Needed: Certificate-Guided Visual Routing for Efficient Diffusion VLMs (115 upvotes) https://huggingface.co/papers/2610.36671 | https://arxiv.org/abs/2610.36671
  Diffusion vision-language models (DVLMs) process their entire input at every denoising step. Since visual tokens make up 89-97% of this input on the benchmarks we study, most of the decoding computation is spent repeatedly processing the same image. Visual token pruning methods partially relieve this burden by removing part of the visual tokens, but they lose the removed information and still proc...
- CoworkOS:Scaling Agent Coworkers for Real-world Automation (95 upvotes) https://huggingface.co/papers/2611.03178 | https://arxiv.org/abs/2611.03178
  Rapid advances in cowork agents are shifting human-AI collaboration toward real-world automation, delivering software, designs, and other artifacts. However, such productivity work demands both high-quality delivery on complex productivity tasks and continued monitoring and decision-making over long horizons, a combination that remains an open challenge. We introduce CoworkOS, a general-purpose ha...
- Route Anything: A Study of Model and Policy Routing for General-Purpose AI Systems (86 upvotes) https://huggingface.co/papers/2611.05275 | https://arxiv.org/abs/2611.05275
  Artificial general intelligence (AGI) requires a method that can understand, generate, reason, and act across diverse domains and modalities. Rather than relying on a single model to master every capability, a promising path toward AGI now is to orchestrate a heterogeneous ecosystem of specialized models, tools, and policies (candidates) into a unified AI system. At the heart of this vision lies a...
- CUA-Master: Scaling Computer-use Agents through Open-World Recursive Improvements (78 upvotes) https://huggingface.co/papers/2611.03126 | https://arxiv.org/abs/2611.03126
  Despite recent advances in CUAs, their development remains constrained by the limited diversity, controllability, and reliability of interaction data. Moreover, conventional optimization pipelines lack iterative feedback, while existing recursive improvement approaches often rely on self-generated experiences, limiting ability expansion and yielding diminishing returns. To address these challenges...
- Youtu-Parsing-Omni: One Encoder, One Schema, All Modalities (76 upvotes) https://huggingface.co/papers/2610.39301 | https://arxiv.org/abs/2610.39301
  We present Youtu-Parsing-Omni, an omni-modal parser that converts documents, images, audio, and video into structured records grounded in space and time, providing a perception layer for agents that read, locate, and cite evidence across modalities. Its design rests on one encoder for every modality and one schema for every task. Youtu-Omni-Encoder, initialized from a pre-trained language model to...
- A-RSI: Adaptive Task Refresh for Zero-Data Multimodal Self-Improvement (75 upvotes) https://huggingface.co/papers/2610.38568 | https://arxiv.org/abs/2610.38568
  Recursive self-improvement requires models not only to acquire useful training experience, but also to decide when their current experience has ceased to be useful. Existing methods often focus on what experience to generate next, while paying less attention to when fresh experience should be introduced. Many also construct training targets through self-consistency or majority voting, making super...
- Video Generation Meets Agent Harness: Agentic Video Generation, Agentic World Modeling and Recursive Self-Improvement (74 upvotes) https://huggingface.co/papers/2610.40191 | https://arxiv.org/abs/2610.40191
  Video generation is shifting from end-to-end synthesis toward agentic generation, where planning, tool use, and feedback enable coherent, controllable multi-shot videos. In parallel, video world models provide action-conditioned observations and predicted futures, serving as interactive environments for agents. We study their intersection through the agent harness: an executable runtime that const...
- Proving and Improving the Platonic Representation Hypothesis with JEPAs (73 upvotes) https://huggingface.co/papers/2610.39302 | https://arxiv.org/abs/2610.39302
  Whether models trained on different modalities converge to the same representation of the world is central to AI. The Platonic Representation Hypothesis (PRH) conjectures that they do as they scale, but without a proof it offers neither a guarantee nor a recipe. We turn the hypothesis into a theorem. First, we prove a Platonic Representation Theorem: Joint-Embedding Predictive Architectures (JEPAs...

## Hacker News top AI stories
- Show HN: HackerBooks – HackerTube, but for books mentioned on HN (1852 points, 306 comments) https://hackerbooks.org | discussion: https://news.ycombinator.com/item?id=50326821
- Postman silently auto-installs AI plugins and attempts to share all API data (1494 points, 485 comments) https://github.com/postmanlabs/postman-app-support/issues/14370 | discussion: https://news.ycombinator.com/item?id=50354960
- AI is forcing us to pay off 40 years of technical debt (1141 points, 662 comments) https://spectrum.ieee.org/ai-in-cybersecurity-php2shell-vulnerability | discussion: https://news.ycombinator.com/item?id=50364336
- Backdoor in Claude Code for VS Code extension on the Cursor Marketplace (1011 points, 553 comments) https://phorion.io/blog/offical-claude-code-vsx-compromise/ | discussion: https://news.ycombinator.com/item?id=50300683
- Show HN: Subvocal – Talk to your computer without making noise (830 points, 390 comments) https://news.ycombinator.com/item?id=50340088 | discussion: https://news.ycombinator.com/item?id=50340088
- AI isn't replacing SREs, it's deskilling them (684 points, 508 comments) https://newsletter.signoz.io/p/ai-isnt-replacing-sres-its-deskilling | discussion: https://news.ycombinator.com/item?id=50305693
- Google will turn off search for schools that reject AI (664 points, 460 comments) https://www.nytimes.com/2026/11/03/us/google-search-schools-restrict-ai.html | discussion: https://news.ycombinator.com/item?id=50353192
- Backdoors in official Claude Code extensions (662 points, 17 comments) https://cyberplace.social/@GossiTheDog/117528831681803563 | discussion: https://news.ycombinator.com/item?id=50302334
- Tell HN: Gemini trains on chat history, even for subscribers (personal accounts) (650 points, 168 comments) https://news.ycombinator.com/item?id=50363461 | discussion: https://news.ycombinator.com/item?id=50363461
- Ubuntu still has not released patch for Linux 0day RCE in almost 3 weeks (624 points, 212 comments) https://freenode.net/article/ubuntu-lts-kernels-still-unfixed-for-critical-cve-2026-98432 | discussion: https://news.ycombinator.com/item?id=50341462
- LLM Voice (610 points, 336 comments) https://martinfowler.com/bliki/LLM-Voice.html | discussion: https://news.ycombinator.com/item?id=50290177
- Fujifilm to boost tape production 5x as AI fuels archiving demand (529 points, 228 comments) https://arstechnica.com/gadgets/2026/10/fujifilm-to-boost-tape-production-5x-as-ai-fuels-archiving-demand/ | discussion: https://news.ycombinator.com/item?id=50336918
- OpenAI seems to be silently re-enabling model training on Codex chats (518 points, 155 comments) https://news.ycombinator.com/item?id=50352757 | discussion: https://news.ycombinator.com/item?id=50352757
- Anthropic blocks users for anything touching training larger models (492 points, 269 comments) https://twitter.com/jiahaoshao1/status/2116475922190922088 | discussion: https://news.ycombinator.com/item?id=50319358
- The AI cost of JavaScript frameworks (476 points, 398 comments) https://nolanlawson.com/2026/10/28/the-ai-cost-of-javascript-frameworks/ | discussion: https://news.ycombinator.com/item?id=50323088