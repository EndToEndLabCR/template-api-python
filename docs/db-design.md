
```mermaid
erDiagram
    USER {
        UUID id
        string email
        
        string first_name
        string last_name
        enum user_role
        enum user_status
        string hashed_password Optional
        
        datetime created_at Optional
        datetime updated_at Optional
    }
```