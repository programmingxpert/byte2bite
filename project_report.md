# Project Report: RecipeAI – Intelligent Food Waste Reduction & Sustainable Gastronomy

**Submitted as part of the 1M1B – IBM SkillsBuild AI + Sustainability Virtual Internship**  
*In Collaboration with IBM SkillsBuild & AICTE*

---

## Project Metadata
* **Project Title**: RecipeAI: Smart Food Preservation, Recipe Matching, and SDG Impact Analytics
* **Primary Developer**: Satyasundar Behera (Alliance University)
* **Lead Researcher**: Aishani Dutta (Alliance University)
* **Academic Institution**: Alliance University
* **Primary SDG Alignment**: **SDG 12 – Responsible Consumption and Production** (Target 12.3: Reduction of consumer food waste)
* **Secondary SDG Alignment**: **SDG 13 – Climate Action** (Reduction of municipal organic waste greenhouse gas emissions)

---

## 1. Problem Statement
> **"How might we use Multimodal Computer Vision and Large Language Models to detect available household ingredients so that consumer food waste is minimized and household meal planning becomes more environmentally sustainable?"**

### The Context of Food Waste
Food waste is a major contributor to global greenhouse gas emissions, representing approximately 8-10% of total global emissions. According to the UN Environment Programme (UNEP) Food Waste Index Report, households are responsible for nearly 60% of all food waste. 

This waste occurs primarily due to:
1. **Lack of Visibility**: Consumers forget what ingredients they already have in their refrigerator.
2. **Spoilage Risk**: Highly perishable ingredients (dairy, fruits, leafy vegetables) are not prioritized and spoil before use.
3. **Inability to Match**: Consumers struggle to think of creative recipes using exact ingredient subsets, leading them to buy more food or discard leftovers.
4. **Poor Sustainability Awareness**: Consumers are unaware of the carbon footprint of their food waste or how to replace high-emission ingredients (like beef or resource-heavy dairy) with lower-impact alternatives.

---

## 2. Detailed Solution Description
**RecipeAI** is an end-to-end web application that leverages a state-of-the-art multimodal AI pipeline to analyze a photo of a user's refrigerator or kitchen counter, extract ingredients, prioritize items close to spoiling, recommend sustainable recipes, and calculate environmental impact metrics.

### Key Capabilities of the Prototype:
1. **Multimodal Ingredient Recognition**: Users upload a photo of their ingredients. A vision model (`qwen3-vl:2b`) detects the ingredients, draws labeled bounding boxes, and populates a digital inventory list.
2. **Interactive Inventory & Spoilage alerts**: The detected list is displayed in a responsive grid. Perishable ingredients (like milk, paneer, and bread) automatically display an eye-catching orange **"Use Soon"** warning badge. Users can add custom ingredients, adjust quantities, or delete items.
3. **Fuzzy Recipe Matching Algorithm**: Calculates recipe matches from a 138-recipe database based on available inventory, sorting by maximum ingredient utilization or match percentage.
4. **IBM Granite Recommendation Engine**: The system sends the available ingredients and top recipe matches to `granite3-dense:2b` via an automated paramiko SSH Tunnel to generate:
   - **SDG 12 Impact Analysis**: An assessment of how the recipe reduces waste.
   - **Sustainability Tips**: Suggestions to substitute high-carbon ingredients or reuse kitchen scraps (e.g., vegetable peels).
5. **AI Kitchen Companion (Chatbot)**: An interactive chat drawer allows users to converse with "Chef Granite" to request recipe variations, storage tips, or ingredient substitutes in real time.
6. **Integrated Shopping List**: Any missing ingredients for a desired recipe can be dispatched to a collapsible sidebar Shopping List drawer with one click.
7. **Cloud Orchestrated / Vercel Ready**: The backend operates in a hybrid mode, automatically establishing SSH tunnels to remote CPU VMs for model execution. All temporary uploads and caches write to `/tmp` directories, making the codebase out-of-the-box deployable to serverless hosting like Vercel.

---

## 3. AI Elements and Tools Used

The system architecture utilizes a dual-model, multimodal pipeline combining local execution with secure cloud virtualization:

| AI Component / Tool | Model / Framework | Role in System |
| :--- | :--- | :--- |
| **Multimodal Vision Model** | `qwen3-vl:2b` (Ollama Cloud / Local) | Takes image files, detects food items, returns ingredient classes, and overlays bounding boxes. |
| **Reasoning & Chat LLM** | `granite3-dense:2b` (Ollama Cloud / Local) | Generates customized recipes, carbon impact explanations, and acts as the conversational backend for the chatbot. |
| **SSH Tunneling Orchestrator** | `paramiko` (Python library) | Automatically forwards remote Ollama sockets from `64.227.167.140:11434` to local port `11435` in cloud mode to bypass Sophos firewalls. |
| **Server-Sent Events (SSE)** | FastAPI Streaming Response | Streams pipeline progress logs (`upload` → `detection` → `matching` → `sustainability` → `ai` → `complete`) to the client. |
| **Web UI Stack** | React Vite + Tailwind CSS + Lucide Icons | Responsive client layout featuring interactive cards, badges, modal dialogs, and slide-out drawers. |
| **Deployment Engine** | Vercel (`vercel.json`) | Packages the static build client and serves the FastAPI backend via serverless functions. |

---

## 4. Prototype Architecture & Code Structure

The project code is organized into a frontend-backend monorepo:

### A. Root Directory Layout
* `recipes.json`: Structured database containing 138 recipes, descriptions, and dietary mappings.
* `recipe_matcher.py`: Performs normalized fuzzy matching to associate detected items with database recipes.
* `sustainability_engine.py`: Computes the carbon footprint (CO2 saved) and waste reduction scores for each match.
* `vision.py`: Executes Qwen-VL model to extract ingredients. Handles image resizing (512x512) in local mode and Base64 API requests in cloud mode.
* `granite.py`: Directs prompts to the Granite reasoning engine, managing in-memory caching to reduce latency.
* `run_dev.bat`: Batch script to run both dev servers with a single click.
* `vercel.json`: Declarative routing configuration for Vercel deployment.

### B. Backend Directory (`/backend`)
* `main.py`: FastAPI server containing SSE streaming pipelines (`/api/analysis-stream`), chat endpoints (`/api/chat`), and CORS middleware.
* `config.py`: Resolves SSH tunneling parameters, handling private keys directly from environment strings (`CLOUD_SSH_KEY`).
* `requirements.txt`: Lightweight list of packages optimized for Vercel functions (excluding heavy libraries like `torch` and `transformers`).

### C. Frontend Directory (`/frontend`)
* `src/App.jsx`: State hub managing active ingredients, shopping list items, dark mode toggles, and chatbot state.
* `src/utils/api.js`: Client-side connector communicating with backend SSE stream.
* `src/components/IngredientsList.jsx`: Grid-based inventory editor featuring perishables warning badges and recalculation controls.
* `src/components/ShoppingList.jsx`: Collapsible drawer tracking user shopping items.
* `src/components/AIRecommendations.jsx`: Renders Granite recommendation cards alongside the Chef Chatbot widget.

---

## 5. Design Thinking Framework

### Stage 1: Empathize
* **Who faces the problem?** Average household members, students living in dorms, and home cooks.
* **What challenges do they experience?** Reopening the fridge multiple times, forgetting what ingredients exist, discarding spoiled milk or vegetables, and lacking culinary inspiration for random subsets of leftovers.
* **Why does the problem persist?** Manual inventory trackers are tedious and quickly abandoned. Static recipe books assume access to a fully stocked pantry.

### Stage 2: Define
* **Core Problem**: Users throw away perfectly edible ingredients because they don't know what to make with them before they spoil.
* **Target Users**: Sustainable-minded home cooks, students, and budget-conscious families.
* **Current Gaps**: Standard recipe websites suggest meals that require buying 5 new ingredients. There is no automated inventory checking or CO2 impact tracking.

### Stage 3: Ideate
* **The Solution**: An app that takes a photo, populates the inventory instantly, flags items that spoil quickly, and queries a language model (`granite3-dense`) to write recipes that *only* focus on using up those soon-to-expire ingredients.

### Stage 4: Prototype
* Created a lightweight visual interface with cards showing ingredients you have and what you need.
* Added a chatbot to allow the user to modify the recipes (e.g. *"I don't have an oven, how can I make this on a tawa?"*).

### Stage 5: Test & Refine
* **User Feedback**: Highly perishable items need more visibility.
* **Refinement**: Implemented **Spoilage alerts** which automatically flag milk, curd, paneer, and bread as "Use Soon".

---

## 6. Responsible AI Considerations (Mandatory)

To align with the IBM SkillsBuild Ethical AI guidelines, RecipeAI implements the following controls:

1. **Fairness**: The ingredient classes (defined in `classes.txt`) are trained on generic vegetables, fruits, and starches, ensuring equal performance regardless of regional brands. The recipe engine supports filters for vegetarian and non-vegetarian preferences to remain inclusive of diverse cultural practices.
2. **Transparency**: Recipe cards explicitly detail *why* they were recommended by displaying the exact matched ingredients and calculating a transparent "Match Score" based on available items.
3. **Privacy & Data Security**: Uploaded images are stored in a temporary `/tmp` folder and deleted when the serverless instance recycles. No facial recognition or metadata tracking is performed.
4. **Safety & Ethics**: The conversational companion "Chef Granite" is system-prompted to restrict its guidance strictly to culinary, food storage, and sustainability advice, preventing harmful or unrelated conversational outputs.

---

## 7. Expected Environmental & Social Impact

If implemented widely, RecipeAI creates direct positive impacts:

* **Environmental Impact (SDG 13)**: The system calculates the CO2 emissions avoided by saving ingredients from the landfill. By using up leftover rice, bread, or vegetables, households reduce methane emissions generated by organic waste decay in local dump sites.
* **Social Impact (SDG 12)**: Enhances resource efficiency and promotes conscious consumption behavior. It teaches young cooks how to store food, substitute ingredients safely, and reduce grocery expenses.

---

## 8. Prototype Screenshots & Demo References

### Image Detection and Bounding Box
Below is an example of an input image uploaded to the vision pipeline, which has been successfully annotated with bounding boxes:
* **Processed Demo Image**: [upload_1782200177539_labeled.png](file:///c:/Projects/RecipeAI/backend/uploads/upload_1782200177539_labeled.png)
* **Sample Input**: [fridge_1.jpeg](file:///c:/Projects/RecipeAI/samples/fridge_1.jpeg)

*Note: In the final application, these bounding boxes are overlaid on the image in real time to show the user exactly what ingredients were identified by the AI.*
