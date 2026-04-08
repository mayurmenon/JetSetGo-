# Travel AI Website Backend README

## Overview

This backend supports the Travel AI Website, which generates optimized itineraries based on user inputs. The backend handles user requests, fetches relevant data from APIs, and integrates with Tinyfish AI to provide smart travel plans.

---

## Features

* Accepts user inputs for trip planning:

  * Destination (city or country)
  * Budget
  * Duration of stay
  * Trip type (Adventure, Relaxation, Foodie, Cultural, Nature, Mixed)

* Processes user input and filters options:

  * Fetches hotel, flight, and attraction data from external APIs.
  * Filters accommodations by cost.
  * Generates optimized itineraries using Tinyfish AI.

* Returns structured JSON responses to the frontend.

---

## Backend Stack

* **Python 3.x**
* **FastAPI** for API handling
* **Uvicorn** for server
* **Requests** for API calls

---

## Endpoints

### `POST /plan-trip`

* Accepts a JSON payload with the following structure:

```json
{
  "destination": "Paris",
  "budget": 800,
  "duration": 5,
  "trip_type": ["Cultural", "Foodie"]
}
```

* Returns JSON with:

  * Cheapest accommodations
  * Suggested itinerary from Tinyfish AI

### `GET /`

* Health check endpoint.
* Returns:

```json
{"status": "Backend running"}
```

---

## Notes for Backend Development

* Validate all input fields.
* Ensure compatibility with the frontend form structure.
* Handle optional fields gracefully.
* Optimize calls to external APIs to prevent rate limit issues.
* Integrate Tinyfish AI for itinerary generation.

---

## Setup Instructions

1. Install dependencies:

```bash
pip install fastapi uvicorn requests
```

2. Run the server:

```bash
uvicorn main:app --reload
```

3. Access health check at `http://127.0.0.1:8000`
4. Test the `/plan-trip` endpoint using Postman or frontend.

---

## Future Enhancements (Not Included Yet)

* User progress tracking (countries visited, places visited)
