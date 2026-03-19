# Jema Backend – File Structure Overview

## Project Overview

The **Jema system** is an AI-powered East African cooking assistant that helps users discover recipes based on their ingredients and dietary preferences. It combines traditional recipe databases with LLM intelligence to provide personalized recipe recommendations and cooking guidance.

---

## Root Directory Files

### `views.py`
**Purpose:** Django REST API endpoints  
Handles HTTP requests and responses for the Jema system. Exposes the JemaEngine to web clients, manages chat sessions, and routes requests to the appropriate handlers. This is the entry point for all API clients.

### `models.py`
**Purpose:** Django database models  
Defines the data structure for storing chat sessions and individual chat messages. Models include:
- `ChatSession`: Stores conversation sessions with user ID and timestamps
- `ChatMessage`: Stores individual messages within a session with role (user/assistant) and timestamps

### `serializers.py`
**Purpose:** Request/response serialization  
Converts Django models to/from JSON using Django REST Framework. Handles serialization of ChatSession and ChatMessage objects for API responses.

### `urls.py`
**Purpose:** URL routing configuration  
Maps HTTP endpoints to view functions. Defines the REST API routes for health checks, creating sessions, sending messages, and retrieving chat history.

### `README.md`
**Purpose:** Project overview and setup guide  
High-level introduction to the Jema project, its features, and basic usage instructions.

### `IMPLEMENTATION_COMPLETE.md`
**Purpose:** Implementation status and completion notes  
Documents phases of development, completed features, known limitations, and migration status between src/ and services/ modules.

### `RECIPE_FORMAT_SHOWCASE.md`
**Purpose:** Example recipe output formats  
Demonstrates the structure and formatting of recipe responses, showing how recipes are presented to end users.

### `__init__.py`
**Purpose:** Django app initialization  
Makes the jema directory a Python package and configures Django app settings (logging, models, etc.).

---

## `services/` Directory

Core business logic and API integration layer. These are stateful, reusable orchestrators that should be called by views.py.

### `jema_engine.py`
**Purpose:** Central orchestrator and state manager  
The main class (`JemaEngine`) that coordinates the entire conversation pipeline. Responsibilities:
- **Intent Classification**: Detects user intent (e.g., ingredient-based, recipe request, information query)
- **Recipe Matching**: Finds relevant recipes from the database
- **Conversation State**: Maintains user context across turns (suggested recipes, rejected recipes, ingredients)
- **Flow Routing**: Directs messages to appropriate handlers based on intent
- **LLM Orchestration**: Delegates to LLMService for advanced queries

Key methods:
- `process_message(user_input)`: Main entry point that returns response dict with message, recipes, language, cta
- `_handle_ingredient_based()`: Matches ingredients to recipes
- `_handle_recipe_request()`: Generates full recipe with steps
- `_handle_greeting()`: Social responses
- `_reset_conversation()`: Clears session state

Has fallback recipes for common East African dishes when database queries don't match.

### `jema_modelling.py`
**Purpose:** Core recommendation and scoring logic  
Contains the machine learning models for recipe matching and ranking. Responsibilities:
- **Recipe Scoring**: Ranks recipes by relevance to user ingredients
- **Nutritional Analysis**: Evaluates recipes against dietary constraints
- **RAG Pipeline**: Retrieval-Augmented Generation for advanced queries
- **Feature Extraction**: Converts ingredients to numerical features for ML models

Used by JemaEngine to enhance recipe recommendations beyond simple database matching.

### `llm_service.py`
**Purpose:** Groq API integration layer  
Handles all LLM (Large Language Model) interactions via Groq API. Responsibilities:
- **Recipe Generation**: Creates custom recipes when not found in database
- **Natural Responses**: Generates conversational, context-aware responses
- **Language Detection**: Detects user language (English/Swahili)
- **Conversation History**: Maintains chat history for multi-turn conversations
- **Prompt Engineering**: Formats prompts with context and guidelines

Key methods:
- `classify_recipe()`: LLM-based recipe classification
- `general_response()`: Generate contextual responses
- `add_to_history()`: Manage conversation history

### `recipe_formatter.py`
**Purpose:** Recipe output formatting  
Transforms raw recipe data into user-friendly formatted responses. Responsibilities:
- **Recipe Assembly**: Combines ingredients, steps, and metadata
- **Text Formatting**: Applies markdown/text formatting for readability
- **Localization**: Adapts recipe format based on language
- **Metadata Inclusion**: Adds cooking time, difficulty, nutrition info

### `response_formatter.py`
**Purpose:** User-facing response formatting  
Formats all responses sent to end users. Responsibilities:
- **Message Formatting**: Creates readable, conversational responses
- **Call-to-Action**: Generates appropriate CTAs based on context
- **Structured Output**: Returns data in consistent format (message, recipes, cta, state)
- **Error Handling**: User-friendly error messages

### `substitute_resolver.py`
**Purpose:** Ingredient substitution and fallback logic  
Handles ingredient variations and substitutions. Responsibilities:
- **Substitution Matching**: Finds similar ingredients when user's item not in database
- **Fallback Recipes**: Returns alternative recipes when exact match fails
- **Semantic Similarity**: Uses ingredient metadata to find close matches
- **Regional Variants**: Understands regional ingredient names (e.g., "sukuma wiki" = "collard greens")

---

## `src/` Directory

Lower-level data processing and utility modules. Partially migrated to services/ but still used by JemaEngine. These are mostly stateless processors.

### `chat.py`
**Purpose:** Chat flow entry point  
Manages conversation flow and message routing. Entry point for chat-based interactions before delegation to JemaEngine.

### `intent_classifier.py`
**Purpose:** Intent detection  
Classifies user messages into intent categories:
- `GREETING`: Introductions, hellos
- `INGREDIENT_BASED`: "I have X, Y, Z"
- `MEAL_IDEA`: "What can I cook?"
- `RECIPE_REQUEST`: "Give me a recipe for X"
- `INFORMATION`: Questions about nutrition, ingredients, cooking
- `REJECTION`: "I don't like that", "No, not that"
- `ACCOMPANIMENT`: "What goes with this?"
- `FOLLOW_UP`: Clarifying questions
- `CHAT_SOCIAL`: Casual conversation

Returns intent, confidence score, constraints extracted from input, and community/cuisine if mentioned.

### `language_detector.py`
**Purpose:** Language detection  
Detects whether user is writing in English or Swahili. Used to:
- Set appropriate response language
- Normalize input (transliterate Swahili text if needed)
- Return responses in user's language

### `ingredient_normalizer_v2.py`
**Purpose:** Ingredient text standardization  
Cleans and standardizes raw ingredient text. Responsibilities:
- **Text Cleaning**: Removes punctuation, extra whitespace
- **Spelling Correction**: Fixes common misspellings
- **Quantity Removal**: Extracts base ingredient names (e.g., "2 cups onion" → "onion")
- **Synonym Mapping**: Maps regional names to standard names
- **Deduplication**: Removes duplicate ingredients from user input

### `excel_recipe_matcher.py`
**Purpose:** Recipe database matching  
Matches normalized ingredients against the recipe dataset. Responsibilities:
- **Exact Matching**: Finds recipes containing all/most user ingredients
- **Partial Matching**: Suggests recipes with some matching ingredients
- **Filtering**: Filters by dietary constraints, cuisine, meal type
- **Ranking**: Orders results by relevance score
- **Metadata Retrieval**: Pulls cooking instructions, nutrition data

### `data_loader.py`
**Purpose:** Recipe dataset loading  
Loads and initializes recipe data from Excel files. Responsibilities:
- **Excel Parsing**: Reads .xlsx recipe datasets
- **Data Validation**: Checks for missing/malformed data
- **Caching**: Loads data once at startup
- **Format Conversion**: Converts to pandas DataFrame for processing

### `llm_service.py` (src)
**Purpose:** Alternative LLM integration (legacy)  
Duplicate of services/llm_service.py. Being migrated to fully use services/ version.

### `recipe_formatter.py` (src)
**Purpose:** Alternative recipe formatter (legacy)  
Duplicate of services/recipe_formatter.py. Being migrated to services/.

### `response_formatter.py` (src)
**Purpose:** Alternative response formatter (legacy)  
Duplicate of services/response_formatter.py. Contains response formatting with CTAFormatter and ResponseType enums.

### `substitute_resolver.py` (src)
**Purpose:** Alternative substitution logic (legacy)  
Duplicate of services/substitute_resolver.py. Being migrated to services/.

---

## `data/` Directory

Recipe database and ingredient datasets.

### `all_ingred.csv`
List of all valid ingredients in the system. Used for ingredient normalization and validation.

### `final_african_recipes.csv`
Curated dataset of African recipes, including East African dishes. CSV version of the main recipe database. Used as fallback when Excel file unavailable.

(Note: Main recipe data is in `Jema_AI_East_Africa_Core_Meals_Phase1.xlsx`, loaded by DataLoader)

---

## `utils/` Directory

Helper utilities and reusable components.

### `csv_detector.py`
**Purpose:** CSV format detection and validation  
Detects and validates CSV files. Used by data loader to handle multiple file format inputs.

### `language_detector.py` (utils)
**Purpose:** Language detection utility  
Lower-level language detection. May be used by intent classifier or message processors.

### `__init__.py`
Makes utils a Python package.

---

## `tests/` Directory

Test suite for the Jema backend.

### `integration_test.py`
**Purpose:** End-to-end integration tests  
Tests the full pipeline from user input to response. Verifies that all components work together correctly, including:
- Intent classification → Recipe matching → LLM integration
- State management across conversation turns
- Error handling and fallback logic

### `test_api.py`
**Purpose:** API endpoint tests  
Tests Django REST API endpoints. Verifies:
- HTTP request/response handling
- Session management
- Message serialization/deserialization
- Error responses

---

## `notebooks/` Directory

Jupyter notebooks for experimentation, analysis, and prototyping.

### `data_prep.ipynb`
**Purpose:** Data preparation and exploration  
Notebook for exploring recipe datasets, cleaning data, and preparing ingredients for the system.

### `modelling.ipynb`
**Purpose:** Model development and training  
Notebook for developing ML models for recipe scoring and recommendation, including feature engineering and model evaluation.

---

## Conversation Flow

### Typical User Journey

1. **User Input** → JemaEngine.process_message()
2. **Language Detection** → Detects English/Swahili
3. **Intent Classification** → Determines what user wants
4. **Route to Handler**:
   - If ingredients provided → Match against recipes (ExcelRecipeMatcher)
   - If recipe request → Generate or retrieve full recipe (LLMService)
   - If information query → Generate contextual response (LLMService)
5. **Ingredient Substitution** → Resolve unknown ingredients (SubstituteResolver)
6. **Format Response** → Convert to user-friendly output (ResponseFormatter)
7. **Add Conversation History** → Save for follow-ups (LLMService.add_to_history)
8. **Return Response** → Dict with message, recipes, language, cta, state

### Key Design Patterns

- **Stateful Engine**: JemaEngine maintains conversation context across turns
- **Modular Handlers**: Different intents routed to specialized handlers
- **Orchestration**: JemaEngine orchestrates rather than implementing all logic
- **Fallbacks**: Common recipes and LLM-generated recipes when database matching fails
- **Language-Aware**: All responses generated/matched in user's detected language

---

## Dependencies

- **Django**: Web framework for REST API
- **Django REST Framework**: API serialization
- **Pandas**: Data manipulation and CSV/Excel processing
- **Groq API**: LLM inference for recipe generation and conversational responses
- **Jupyter**: Notebook-based experimentation

---

## Quick Reference: Which File to Modify?

| Task | File(s) |
|------|---------|
| Add new API endpoint | `views.py` |
| Change database schema | `models.py`, `serializers.py` |
| Add conversation handler | `services/jema_engine.py`, `src/intent_classifier.py` |
| Improve recipe matching | `src/excel_recipe_matcher.py` or `services/jema_modelling.py` |
| Change LLM prompts | `services/llm_service.py` |
| Adjust response format | `services/response_formatter.py` |
| Add ingredient mapping | `src/ingredient_normalizer_v2.py` or `services/substitute_resolver.py` |
| Add new recipe data | `data/` directory |
| Test new feature | `tests/` directory |

---

## Architecture Diagram

```
┌─────────────────────────────────────┐
│      Django REST API (views.py)     │
│         HTTP Endpoints              │
└────────────────┬────────────────────┘
                 │
                 ▼
        ┌────────────────────┐
        │   JemaEngine       │
        │  (Orchestrator)    │
        │                    │
        │ • State management │
        │ • Intent routing   │
        │ • Response building│
        └──┬──────────────┬──┘
           │              │
      ┌────▼──────┐   ┌──▼──────────┐
      │  Intent   │   │Conversation │
      │Classifier │   │   History   │
      └────┬──────┘   └──┬──────────┘
           │             │
    ┌──────▼──────┬──────▼───────┐
    │   Recipe    │   LLM        │
    │   Matching  │   Service    │
    │             │              │
    │  •Normalize │  •Generate   │
    │  •Match     │  •Respond    │
    │  •Rank      │  •Translate  │
    └──────┬──────┴──────┬───────┘
           │             │
      ┌────▼─────────────▼────┐
      │   Recipe Database     │
      │   (Excel + CSV)       │
      └───────────────────────┘
```

