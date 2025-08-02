# AI Agent Giải Thuật - System Pipeline Diagrams

## 1. Document Processing and Indexing Pipeline

```mermaid
flowchart TD
    A[User Uploads Document] --> B[Document Validation]
    B --> C{File Type Check}
    C -->|PDF| D[PDF Loader]
    C -->|DOCX| E[DOCX Loader]
    C -->|TXT| F[Text Loader]
    C -->|Unsupported| G[Error Response]

    D --> H[Text Extraction]
    E --> H
    F --> H

    H --> I[Text Standardization]
    I --> J[Recursive Text Splitting]
    J --> K[Chunk Processing]
    K --> L[Metadata Addition]
    L --> M[Vector Embedding Generation]
    M --> N[Pinecone Vector Store]
    N --> O[Document Status Update]
    O --> P[Success Response]

    G --> Q[Error Handling]
    Q --> R[Status: Failed]

    style A fill:#e1f5fe
    style N fill:#f3e5f5
    style P fill:#e8f5e8
    style R fill:#ffebee
```

## 2. Course and Lesson Generation Pipeline

```mermaid
flowchart TD
    A[Admin Creates Course] --> B[Course Configuration]
    B --> C[Topic Selection]
    C --> D[Lesson Generation Request]
    D --> E[Lesson Generating Agent]

    E --> F[Context Retrieval from Pinecone]
    F --> G[Topic Information Gathering]
    G --> H[Lesson Structure Generation]
    H --> I[Content Generation for Each Section]

    I --> J{Section Type}
    J -->|Text| K[Theoretical Content]
    J -->|Code| L[Code Examples]
    J -->|Quiz| M[Interactive Questions]

    K --> N[Content Validation]
    L --> N
    M --> N

    N --> O[Lesson Schema Creation]
    O --> P[Database Storage]
    P --> Q[Course Structure Update]
    Q --> R[Success Response]

    style A fill:#e1f5fe
    style E fill:#fff3e0
    style P fill:#f3e5f5
    style R fill:#e8f5e8
```

## 3. Exercise Generation and Management Pipeline

```mermaid
flowchart TD
    A[User Requests Exercise] --> B[Exercise Generation Agent]
    B --> C[Topic Analysis]
    C --> D[Algorithm Vault Retrieval]
    D --> E[Existing Exercise Check]
    E --> F{Exercise Exists?}

    F -->|Yes| G[Return Existing Exercise]
    F -->|No| H[Generate New Exercise]

    H --> I[Exercise Content Creation]
    I --> J[Difficulty Level Assignment]
    J --> K[Input/Output Format Definition]
    K --> L[Constraints Specification]
    L --> M[Example Generation]
    M --> N[Hint Creation]
    N --> O[Output Parser Validation]
    O --> P[Exercise Storage]
    P --> Q[Response to User]

    G --> Q

    style A fill:#e1f5fe
    style B fill:#fff3e0
    style P fill:#f3e5f5
    style Q fill:#e8f5e8
```

## 4. Test Generation and Assessment Pipeline

```mermaid
flowchart TD
    A[Admin Initiates Test Generation] --> B[Test Generation Service]
    B --> C[Course Topic Analysis]
    C --> D[Input Test Agent]
    D --> E[Question Generation]
    E --> F[Question Classification]
    F --> G[Difficulty Distribution]
    G --> H[Test Structure Creation]
    H --> I[Database Storage]
    I --> J[Test Session Creation]
    J --> K[User Notification]

    L[User Takes Test] --> M[Test Session Management]
    M --> N[Question Presentation]
    N --> O[Answer Collection]
    O --> P[Score Calculation]
    P --> Q[Assessment Agent]
    Q --> R[Performance Analysis]
    R --> S[Learning Path Generation]
    S --> T[Personalized Recommendations]

    style A fill:#e1f5fe
    style B fill:#fff3e0
    style Q fill:#fff3e0
    style T fill:#e8f5e8
```

## 5. AI Chat and Tutoring Pipeline

```mermaid
flowchart TD
    A[User Submits Code] --> B[Code Execution]
    B --> C[Test Case Execution]
    C --> D[Result Analysis]
    D --> E[AI Chat Agent]

    E --> F{User Message Type}
    F -->|Question| G[Context Retrieval]
    F -->|Code Review| H[Code Analysis]

    G --> I[Conversation History]
    H --> J[Error Detection]
    J --> K[Solution Generation]
    I --> L[Response Generation]
    K --> L

    L --> M[Response Validation]
    M --> N[User Response]

    O[Tutor Agent] --> P[Exercise Context]
    P --> Q[Student Performance Analysis]
    Q --> R[Personalized Guidance]
    R --> S[Learning Recommendations]
    S --> T[Progress Tracking]

    style A fill:#e1f5fe
    style E fill:#fff3e0
    style O fill:#fff3e0
    style T fill:#e8f5e8
```

## 6. Learning Progress and Assessment Pipeline

```mermaid
flowchart TD
    A[Student Learning Session] --> B[Topic Selection]
    B --> C[Lesson Access]
    C --> D[Content Consumption]
    D --> E[Exercise Attempt]
    E --> F[Code Submission]
    F --> G[Execution Engine]
    G --> H[Result Evaluation]

    H --> I{All Tests Pass?}
    I -->|Yes| J[Progress Update]
    I -->|No| K[Error Analysis]

    K --> L[AI Chat Support]
    L --> M[Guidance Provision]
    M --> N[Retry Attempt]
    N --> F

    J --> O[Topic Completion Check]
    O --> P{All Topics Complete?}
    P -->|Yes| Q[Course Completion]
    P -->|No| R[Next Topic Recommendation]

    Q --> S[Certificate Generation]
    R --> B

    style A fill:#e1f5fe
    style G fill:#fff3e0
    style L fill:#fff3e0
    style S fill:#e8f5e8
```

## 7. User Authentication and Authorization Pipeline

```mermaid
flowchart TD
    A[User Registration/Login] --> B[Credential Validation]
    B --> C{Authentication Method}
    C -->|Email/Password| D[Password Verification]
    C -->|OAuth| E[OAuth Provider]

    D --> F[Token Generation]
    E --> F
    F --> G[JWT Token Creation]
    G --> H[User Session Management]
    H --> I[Role Assignment]
    I --> J[Permission Validation]
    J --> K[Access Control]
    K --> L[API Response]

    M[Request with Token] --> N[Token Validation]
    N --> O[User Context Extraction]
    O --> P[Permission Check]
    P --> Q[Resource Access]
    Q --> R[Response Generation]

    style A fill:#e1f5fe
    style F fill:#fff3e0
    style Q fill:#f3e5f5
    style R fill:#e8f5e8
```

## 8. Discussion and Community Pipeline

```mermaid
flowchart TD
    A[User Creates Discussion] --> B[Content Validation]
    B --> C[Topic Classification]
    C --> D[Database Storage]
    D --> E[Notification System]
    E --> F[Community Engagement]

    G[User Replies] --> H[Reply Processing]
    H --> I[Content Moderation]
    I --> J[Reply Storage]
    J --> K[Thread Update]
    K --> L[Notification Dispatch]

    M[Discussion Search] --> N[Query Processing]
    N --> O[Content Retrieval]
    O --> P[Relevance Ranking]
    P --> Q[Search Results]

    style A fill:#e1f5fe
    style D fill:#f3e5f5
    style J fill:#f3e5f5
    style Q fill:#e8f5e8
```

## 9. Admin Management Pipeline

```mermaid
flowchart TD
    A[Admin Login] --> B[Admin Authentication]
    B --> C[Admin Dashboard Access]
    C --> D{Admin Action}

    D -->|Course Management| E[Course CRUD Operations]
    D -->|User Management| F[User CRUD Operations]
    D -->|Content Management| G[Content CRUD Operations]
    D -->|System Monitoring| H[Analytics Dashboard]

    E --> I[Course Validation]
    F --> J[User Validation]
    G --> K[Content Validation]
    H --> L[Data Aggregation]

    I --> M[Database Update]
    J --> M
    K --> M
    L --> N[Report Generation]

    M --> O[Success Response]
    N --> P[Admin Notification]

    style A fill:#e1f5fe
    style C fill:#fff3e0
    style M fill:#f3e5f5
    style O fill:#e8f5e8
```

## 10. System Integration and Data Flow

```mermaid
flowchart TD
    A[Frontend Application] --> B[API Gateway]
    B --> C[Authentication Middleware]
    C --> D[Request Routing]
    D --> E{Service Type}

    E -->|User Service| F[User Management]
    E -->|Course Service| G[Course Management]
    E -->|AI Service| H[AI Agent Processing]
    E -->|Assessment Service| I[Assessment Processing]
    E -->|Document Service| J[Document Processing]

    F --> K[Database Operations]
    G --> K
    H --> L[AI Model Processing]
    I --> M[Analytics Processing]
    J --> N[Vector Store Operations]

    K --> O[Response Generation]
    L --> O
    M --> O
    N --> O

    O --> P[Response Middleware]
    P --> Q[Frontend Update]

    style A fill:#e1f5fe
    style B fill:#fff3e0
    style K fill:#f3e5f5
    style Q fill:#e8f5e8
```

## Key Components and Technologies

### AI Agents

- **Exercise Generation Agent**: Creates algorithm exercises using RAG
- **Assessment Agent**: Analyzes test results and generates learning paths
- **Lesson Generating Agent**: Creates educational content using RAG
- **AI Chat Agent**: Provides real-time tutoring support
- **Tutor Agent**: Offers personalized guidance

### Data Storage

- **PostgreSQL**: Primary database for user data, courses, tests
- **Pinecone**: Vector store for document embeddings and RAG
- **MongoDB**: Chat history and conversation management

### Core Services

- **Authentication Service**: JWT-based user authentication
- **Course Service**: Course and lesson management
- **Test Service**: Test generation and assessment
- **Document Service**: Document processing and indexing
- **Assessment Service**: Learning progress analysis

### Frontend Integration

- **Next.js**: React-based frontend application
- **Real-time Chat**: WebSocket-based AI chat interface
- **Code Editor**: Monaco Editor for code execution
- **Progress Tracking**: Real-time learning progress updates

This comprehensive pipeline architecture ensures seamless integration between all components while maintaining scalability and performance for the AI-powered learning platform.
