# Akademiya API Contract

## Base URL
- `http://<host>/`

## Global Request Guidelines
- Use `Content-Type: application/json` for JSON bodies.
- Use `Accept: application/json` for JSON responses.
- For any frontend request that uses cookies, always send `credentials: include`.
- For any state-changing request (`POST`, `PUT`, `PATCH`, `DELETE`), include the CSRF token in `X-CSRFToken`.
- If using cookies, call `GET /users/csrf/` first to populate the CSRF cookie.

## Authentication

### Authentication model
- The app uses Django session authentication.
- Login is handled by OTP flow and maintains a browser cookie session.
- `GET /users/me/` checks current session state.
- `POST /users/logout/` clears the session.

### GET /users/csrf/
- Description: Initialize CSRF protection for the frontend.
- Request: no body
- Response:
  - `200 OK`
  - Body:
    ```json
    {"detail": "CSRF cookie set."}
    ```
- Frontend usage:
  - Call before any authenticated request that changes server state.
  - The browser will receive a `csrftoken` cookie.

### POST /users/otp_request/
- Description: Request a one-time password (OTP) for email login.
- Request Body:
  ```json
  {
    "email": "user@example.com"
  }
  ```
- Response:
  - `200 OK` on success
  - `400 Bad Request` if the payload is invalid
- Notes:
  - The request should include `credentials: include` if the frontend wants to preserve session cookies.
  - The API sends the OTP email but does not return the OTP in the response.

### POST /users/otp_verification/
- Description: Verify the OTP and authenticate the user.
- Request Body:
  ```json
  {
    "email": "user@example.com",
    "otp": 123456
  }
  ```
- Response Body on success:
  ```json
  {
    "detail": "Authentication successful.",
    "authenticated": true,
    "user": {
      "id": 1,
      "email": "user@example.com",
      "username": "generated_username",
      "is_staff": false
    }
  }
  ```
- Response codes:
  - `200 OK` on success
  - `400 Bad Request` if OTP is invalid or payload is invalid
  - `403 Forbidden` if the user account is inactive
- Notes:
  - Creates a new `Scholar` if no existing user is found.
  - The session cookie is set on successful login.
  - Use `credentials: include` and pass `X-CSRFToken` if the frontend is browser-based.

### GET /users/me/
- Description: Get the current authenticated user.
- Response Body:
  - Authenticated:
    ```json
    {
      "authenticated": true,
      "user": {
        "id": 1,
        "email": "user@example.com",
        "username": "generated_username",
        "is_staff": false
      }
    }
    ```
  - Not authenticated:
    ```json
    {
      "authenticated": false,
      "user": null
    }
    ```
- Response codes:
  - `200 OK` when authenticated
  - `401 Unauthorized` when not authenticated
- Notes:
  - Use `credentials: include` so the backend can read the session cookie.

### POST /users/logout/
- Description: Log out the current user and clear the session.
- Request Body: none
- Response Body:
  ```json
  {
    "detail": "Logged out successfully."
  }
  ```
- Response codes:
  - `200 OK`
- Notes:
  - Send `credentials: include` and `X-CSRFToken` when calling from the frontend.

### Allauth routes
- `GET/POST /users/accounts/...`
- Description: Standard Django Allauth authentication and account management endpoints.
- Notes:
  - These are available for additional auth methods beyond OTP.
  - The frontend may use them for email/password, social login, or account management as needed.

## Authenticated request behavior
- `401 Unauthorized`: returned when the request is not authenticated.
- `403 Forbidden`: returned when the authenticated user lacks permission.
- Use `credentials: include` on all requests that rely on session authentication.
- Set `X-CSRFToken` with the value from the `csrftoken` cookie for POST/PUT/PATCH/DELETE.

## Profiles

### GET /profiles/{pk}/
- Description: Retrieve a scholar profile by `pk`.
- Authentication: optional
- Parameters:
  - `pk` (path): scholar ID
- Response Body:
  ```json
  {
    "profile_info": {
      "id": 1,
      "username": "john",
      "photo": "/media/path.jpg",
      "semester": 3,
      "bio": "sample bio",
      "subscribed": false,
      "gems": 100,
      "is_staff": false,
      "is_active": true
    },
    "performance_info": {
      "id": 1,
      "level": 2,
      "experience": 120,
      "attempted": 3,
      "correct": 2,
      "correct_ratio": 66.6667
    },
    "follower_count": 5,
    "followee_count": 2,
    "followers": [
      {"id": 10, "username": "alice"}
    ],
    "followees": [
      {"id": 12, "username": "bob"}
    ]
  }
  ```
- Response codes:
  - `200 OK` on success
  - `404 Not Found` if the scholar does not exist

### PUT /profiles/update/
- Description: Update the authenticated scholar's profile.
- Authentication: Required
- Request Body (partial updates allowed):
  ```json
  {
    "username": "newname",
    "photo": "<uploaded file>",
    "semester": 4,
    "bio": "Updated biography"
  }
  ```
- Response:
  - `200 OK` with updated scholar data
  - `400 Bad Request` if validation fails
- Notes:
  - Use `credentials: include` and `X-CSRFToken`.

## Store

### POST /store/subscription/
- Description: Purchase a subscription using gems.
- Authentication: Required
- Request Body: none
- Response Body:
  ```json
  {
    "subscribed": true,
    "gems": 300
  }
  ```
- Error Responses:
  - `400 Bad Request` if the scholar has fewer than 700 gems
  - `200 OK` if already subscribed
- Notes:
  - Use `credentials: include` and `X-CSRFToken`.

## Game

### POST /game/start/
- Description: Begin a game session and build a quiz plan.
- Request Body:
  - `mode` required: one of `select`, `custom`, `all`
  - `order` optional: `asc` or `desc`

#### select mode
  ```json
  {
    "mode": "select",
    "subject": {"id": 1, "pages": 5},
    "order": "desc"
  }
  ```

#### custom mode
  ```json
  {
    "mode": "custom",
    "subjects": [
      {"id": 1, "pages": 3},
      {"id": 2, "pages": 4}
    ],
    "order": "desc"
  }
  ```

#### all mode
  ```json
  {
    "mode": "all",
    "pages": 10,
    "order": "desc"
  }
  ```
- Response Body:
  ```json
  {
    "session_id": 5,
    "quiz_plan_id": 7,
    "message": "Game started successfully"
  }
  ```
- Error Responses:
  - `400 Bad Request` when required fields are missing or invalid
  - `404 Not Found` when referenced subjects do not exist

### GET /game/semesters/
- Description: Retrieve all semesters.
- Response Body:
  ```json
  [
    {"id": 1, "name": "Semester 1"}
  ]
  ```

### GET /game/subjects/{semester_id}/
- Description: Retrieve subjects for a semester.
- Path Parameter:
  - `semester_id` integer
- Response Body:
  ```json
  [
    {"id": 1, "name": "Mathematics"}
  ]
  ```
- Errors:
  - `404 Not Found` if semester does not exist

### POST /game/pages_counts/
- Description: Count pages for the requested subjects.
- Request Body:
  ```json
  {
    "subjects": [
      {"subject_name": "Mathematics", "id": 1},
      {"subject_name": "Physics", "id": 2}
    ]
  }
  ```
- Response Body:
  ```json
  {
    "Mathematics": 12,
    "Physics": 8
  }
  ```

### POST /game/submit_answer/
- Description: Submit answers for a game session page.
- Request Body:
  ```json
  {
    "game_session_id": 1,
    "answers": [
      {"answer_id": 1},
      {"answer_id": 2}
    ]
  }
  ```
- Response Body:
  ```json
  {
    "correct_answers": 1,
    "index_no": 2
  }
  ```
- Errors:
  - `400 Bad Request` or `404 Not Found` if the session or answers are invalid

### GET /game/view_question_pages/{game_session_id}/
- Description: Retrieve the question pages assigned to a quiz plan.
- Response Body:
  ```json
  [
    {"id": 10, "subject": {"id": 1, "name": "Math"}, "year": "2025-01-01"}
  ]
  ```

### GET /game/view_question_page/{page_id}/
- Description: Retrieve full details for a question page.
- Response Body:
  ```json
  {
    "id": 10,
    "subject": {"id": 1, "name": "Mathematics"},
    "year": "2025-01-01",
    "questions": [
      {
        "id": 20,
        "description": "What is 2+2?",
        "hint": "Think addition",
        "full_explaination": "2+2 equals 4",
        "answers": [
          {"id": 100, "description": "4", "correct": true},
          {"id": 101, "description": "3", "correct": false}
        ]
      }
    ]
  }
  ```
- Error Responses:
  - `404 Not Found` if the `QuestionPage` is missing

- Description: Delete guest game sessions only.
- Response:
  - `200 OK` on success
  - `400 Bad Request` if the session belongs to an authenticated user
  - `404 Not Found` if session is missing

### POST /game/display_and_update_performance/
- Description: Calculate and update scholar performance after a game.
- Authentication: Required
- Response Body:
  ```json
  {
    "experience": 230,
    "attempted": 20,
    "correct_answers": 5,
    "level": 2
  }
  ```
- Notes: Deletes the game session after processing.

## Admin Tool
> All admin tool endpoints require authenticated admin users.

### POST /admintool/enter_page/
- Description: Add a semester, subject, question page, questions, and answers.
- Request Body Example:
  ```json
  {
    "semester": {"name": "Semester 1"},
    "subject": {"name": "Mathematics"},
    "question_page": {"year": "2025-01-01"},
    "question_answers": [
      {
        "description": "What is 2+2?",
        "hint": "Sum two numbers",
        "full_explaination": "2+2 equals 4",
        "answers": [
          {"description": "4", "correct": true},
          {"description": "3", "correct": false}
        ]
      }
    ]
  }
  ```
- Response:
  - `201 Created` on success
  - `400 Bad Request` with validation errors

### GET /admintool/view_page/{year}/{subject_id}/
- Description: Retrieve a page and its related semester and subject data.
- Response Body: structured page data with question/answer details.

### PUT /admintool/update_page/{year}/{subject_id}/
- Description: Update an existing page, subject, semester, questions, and answers.
- Request Body Example:
  ```json
  {
    "page": {"year": "2025-01-01"},
    "subject": {"name": "Mathematics"},
    "semester": {"name": "Semester 1"},
    "question_answers": [
      {
        "id": 20,
        "description": "Updated question",
        "hint": "...",
        "full_explaination": "...",
        "answers": [
          {"id": 100, "description": "4", "correct": true}
        ]
      }
    ]
  }
  ```
- Response:
  - `200 OK` on success
  - `400 Bad Request` if validation fails

### DELETE /admintool/delete_page/{year}/{subject_id}/
- Description: Delete a specific question page.
- Response:
  - `204 No Content` on success

### GET /admintool/semesters/
- Description: Retrieve all semesters.
- Response: list of semesters

### GET /admintool/subjects/{semester_id}/
- Description: Retrieve subjects for a semester.
- Error:
  - `404 Not Found` if semester does not exist

## Leaderboard

### GET /leaderboard/
- Description: Retrieve the top 10 scholars ordered by performance level.
- Response Body:
  ```json
  [
    {"username": "john", "level": 10}
  ]
  ```

## Data Models Summary

### Scholar
- `id`
- `username`
- `email`
- `photo`
- `semester`
- `bio`
- `subscribed`
- `gems`
- `is_staff`
- `is_active`

### Performance
- `level`
- `experience`
- `attempted`
- `correct`
- `correct_ratio`

### Semester
- `id`
- `name`

### Subject
- `id`
- `name`
- `semester`

### QuestionPage
- `id`
- `subject`
- `year` (ISO date)

### Question
- `id`
- `description`
- `hint`
- `full_explaination`
- `answers`

### Answer
- `id`
- `description`
- `correct`

## Notes
- Authentication is required for profile update, store subscription purchase, performance update, and admin tool endpoints.
- Admin endpoints require admin user privileges.
- The project includes Django Allauth under `/users/accounts/` for standard account flows.
