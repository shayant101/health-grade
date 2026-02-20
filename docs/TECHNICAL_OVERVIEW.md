# Restaurant Grader Technical Overview

## 1. Application Overview

RestaurantGrader is a comprehensive digital health analysis platform for restaurants, providing instant insights into their online presence, digital performance, and potential areas of improvement. The application leverages advanced web scraping, API integrations, and AI-driven analysis to generate actionable recommendations for restaurant owners.

## 2. Architecture Overview

### High-Level System Architecture

- **Frontend**: React-based Single Page Application (SPA)
- **Backend**: FastAPI Python microservice
- **Database**: MongoDB (via Motor async driver)
- **Task Queue**: Celery with Redis broker
- **Deployment**: Containerized microservices

### Component Interaction Flow
1. User initiates restaurant scan via web interface
2. Frontend sends request to FastAPI backend
3. Backend orchestrates multi-stage analysis:
   - Website scraping
   - Google Business Profile analysis
   - Reviews aggregation
   - Ordering system evaluation
4. Celery workers process background tasks
5. Results compiled and scored
6. Insights presented to user

## 3. Frontend Stack

### Framework & Core Technologies
- **Framework**: React (v18.3.1)
- **Language**: TypeScript
- **Build Tool**: Vite (v5.4.19)
- **Routing**: React Router (v6.30.1)

### UI Libraries
- **Component Library**: shadcn/ui (Radix UI primitives)
- **Styling**: Tailwind CSS (v3.4.17)
- **Animation**: Framer Motion (v12.24.7)

### Key Frontend Dependencies
- **State Management**: React Query (v5.83.0)
- **Form Handling**: React Hook Form (v7.61.1)
- **Validation**: Zod (v3.25.76)
- **Icons**: Lucide React
- **Routing**: React Router DOM

### Component Structure
- `/src/components/`: Reusable UI components
  - `SearchForm.tsx`: Restaurant search interface
  - `RestaurantConfirmation.tsx`: Restaurant verification
  - `ScanProgress.tsx`: Scan progress tracking
  - `ResultsDashboard.tsx`: Detailed scan results
  - `LeadCaptureModal.tsx`: Lead generation modal

## 4. Backend Stack

### Framework & Core Technologies
- **Framework**: FastAPI (v0.109.0)
- **Language**: Python 3.9+
- **ASGI Server**: Uvicorn (v0.27.0)
- **ORM**: Pydantic (v2.6.1) for data validation
- **Database Driver**: Motor (Async MongoDB driver)

### Database
- **Type**: MongoDB
- **ORM/Validation**: SQLAlchemy-like Pydantic models
- **Connection Management**: Async database lifecycle in `main.py`

### Task Processing
- **Task Queue**: Celery (v5.3.6)
- **Message Broker**: Redis (v5.0.1)
- **Async Processing**: Background task handling for complex scans

### Key Backend Dependencies
- **Web Scraping**: BeautifulSoup4 (v4.12.3)
- **HTTP Requests**: HTTPX (v0.26.0)
- **Email Services**: Resend (v0.7.0)
- **AI Integration**: OpenAI (v1.12.0)
- **Natural Language Processing**: TextBlob (v0.17.1)

### API Structure
- Modular route organization in `/backend/app/routes/`
  - `restaurants.py`
  - `scans.py`
  - `leads.py`

### Service Layer
- Specialized analyzers in `/backend/app/services/`:
  - `website_analyzer.py`
  - `google_analyzer.py`
  - `reviews_analyzer.py`
  - `ordering_analyzer.py`
  - `scan_orchestrator.py`

## 5. External APIs & Services

### Integrated Services
- **Google Places API**: Comprehensive restaurant profile and location data
  - Retrieve business details
  - Search for restaurant information
  - Access business ratings, reviews, and contact information
  - Validate and enrich restaurant data

- **Google PageSpeed Insights API**: Comprehensive website performance analysis (✅ Fully Integrated)
  - **Performance Score**: Measures loading speed, interactivity, and visual stability (0-100)
  - **Accessibility Score**: Evaluates website accessibility for all users (0-100)
  - **Best Practices Score**: Checks adherence to modern web standards (0-100)
  - **SEO Score**: Assesses search engine optimization quality (0-100)
  - **Loading Time Metrics**: Time to Interactive (TTI) in milliseconds
  - **Multi-Category Analysis**: Requests all categories in parallel for efficiency
  - **Graceful Degradation**: Falls back to Playwright-only analysis if API fails
  - **Smart Timeout**: 90-second timeout handles slow websites
  - See `docs/PAGESPEED_INTEGRATION.md` for complete documentation

- **OpenAI/LLM API**: AI-powered narrative generation
  - Generate contextual insights
  - Create actionable recommendations
  - Provide natural language analysis of digital performance
  - Offer personalized improvement suggestions

- **Playwright**: Headless browser automation for web scraping
  - Perform dynamic website analysis
  - Check mobile responsiveness
  - Extract website metadata
  - Validate website functionality

- **Resend**: Transactional email services
  - Send scan results
  - Deliver error notifications
  - Manage lead communication

## 6. User Flow

### Comprehensive Scanning Process
1. **Restaurant Search**
   - User enters restaurant name and location
   - System validates and confirms restaurant details

2. **Background Scan Initiation**
   - Celery task triggered for comprehensive analysis
   - Parallel processing of multiple analysis streams:
     * Website performance scan (Playwright + PageSpeed)
     * Google Business Profile retrieval
     * Reviews aggregation and sentiment analysis
     * Online ordering system detection

3. **Multi-Dimensional Analysis**
   - Website Analysis
     * Performance scoring
     * Mobile responsiveness check
     * SEO preliminary evaluation
   - Google Business Profile Analysis
     * Profile verification status
     * Review aggregation
     * Posting frequency assessment
   - Reviews Analysis
     * Sentiment scoring
     * Review response rate
     * Thematic insights extraction
   - Ordering System Analysis
     * Online ordering capabilities
     * Integration quality assessment
     * Platform diversity

4. **Scoring and Narrative Generation**
   - Comprehensive score calculation
   - AI-powered narrative generation
   - Actionable improvement recommendations

5. **Results Presentation**
   - Detailed results dashboard
   - Graphical score representation
   - Insights and opportunities
   - Lead capture modal for full report

6. **Follow-up**
   - Email delivery of full report
   - Optional consultation scheduling

## 7. Technology Deep Dive

### Playwright Configuration and Usage
- **Browser Management**
  - Async browser context creation
  - Headless browser automation
  - Cross-browser compatibility
- **Website Analysis Techniques**
  - Dynamic content rendering
  - Mobile viewport simulation
  - Element interaction and extraction
  - Performance and accessibility checks

### Google Places API Integration
- **Authentication**
  - Secure API key management
  - Rate limit handling
- **Search and Details Retrieval**
  - Fuzzy matching of restaurant names
  - Geolocation-based search refinement
  - Comprehensive business profile extraction

### PageSpeed API Integration
- **Performance Metrics**
  - Lighthouse performance scoring
  - Mobile and desktop strategy support
  - Detailed audit insights
- **Key Performance Indicators**
  - Loading time
  - Accessibility score
  - SEO performance
  - Best practices evaluation

### LLM Prompt Engineering
- **Narrative Generation**
  - Contextual prompt design
  - Temperature and token management
  - Multi-step insight generation
- **Recommendation Extraction**
  - Structured output parsing
  - Focus area identification
  - Actionable suggestion creation

### Celery Task Orchestration
- **Distributed Task Processing**
  - Background job management
  - Retry and error handling
  - Scalable task execution
- **Task Workflow**
  - Parallel analysis streams
  - Result aggregation
  - Evidence storage
  - Notification dispatching

## 8. Development Methodologies

### Project Structure Patterns
- Modular, separation of concerns
- Async-first design
- Type-driven development with Pydantic

### API Design Patterns
- RESTful endpoint design
- Comprehensive error handling
- Async route handlers

### Async Task Processing
- Celery for distributed task queue
- Background job management
- Scalable task execution

### Error Handling Approaches
- Global exception middleware
- Detailed logging
- Graceful error responses

## 9. Data Models

### Core Entities

#### Restaurant Model
- Comprehensive restaurant information
- Geolocation support
- Contact information tracking

#### Scan Model
- Multi-dimensional analysis tracking
- Detailed subscore storage
- Flexible metadata support

#### Lead Model
- Multi-source lead generation
- Status-based lead tracking
- Communication log integration

## 10. Future Roadmap
- Enhanced AI narrative generation
- More granular scoring algorithms
- Expanded external service integrations
- Machine learning-driven recommendations
- Advanced sentiment and trend analysis

---

**Generated**: 2026-01-22
**Version**: 0.2.0