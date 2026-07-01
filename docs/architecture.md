# API Sample Project - Architecture Documentation

## 🛠️ Layer Dependencies

### Domain Layer (Core)

- **No external dependencies**
- Contains business entities and value objects
- Defines domain interfaces (repository ABCs)
- Pure business logic

### Application Layer

- **Depends on**: Domain Layer
- Contains use cases and DTOs
- Orchestrates domain objects
- Application mappers (standalone functions: `to_xxx_response`)

### Infrastructure Layer

- **Depends on**: Domain (implements repository interfaces)
- SQLAlchemy models, repository implementations
- Infrastructure mappers (classes with `@staticmethod`: `XxxModelMapper.to_entity` / `XxxModelMapper.to_model`)
- Database connection, external services

### Presentation Layer

- **Depends on**: Application + Domain (via composition root)
- FastAPI routes and dependency injection
- Request/Response handling

### Composition Root (`src/app/composition/`)

- Factory functions for all dependencies
- Centralizes wiring between layers
- Routes import use cases directly from the composition root
- Each feature has its own factory module (`composition/features/<name>.py`)

## 📁 Feature Structure

Only two features exist: **auth** and **user**.

```
src/app/features/{feature}/
├── application/
│   ├── dtos/              # Pydantic request/response models
│   ├── mappers/           # Entity ↔ DTO conversion (standalone functions)
│   └── use_cases/         # Business orchestration classes
├── domain/
│   ├── entities/          # Business objects
│   ├── exceptions/        # Domain-specific errors
│   ├── repositories/      # Repository interfaces (ABC)
│   └── value_objects/     # Immutable domain values (Email, Password, UserRole)
├── infrastructure/
│   ├── mappers/           # Model ↔ Entity conversion (standalone classes)
│   ├── models/            # SQLAlchemy models
│   └── repositories/      # Repository implementations
└── presentation/
    └── {feature}_routes.py # FastAPI routes

## 📊 Architecture Benefits

### ✅ Maintainability

- **Clear separation** of concerns
- **Modular design** enables easy modifications
- **Testable architecture** with dependency injection

### ✅ Scalability

- **Feature-based** organization supports team scaling
- **Clean interfaces** enable parallel development
- **Modular deployment** options

### ✅ Testability

- **Pure business logic** in domain layer
- **Mockable interfaces** for isolated testing
- **Clear test boundaries** between layers

### ✅ Flexibility

- **Framework independence** in business logic
- **Database agnostic** domain layer
- **Easy integration** with external services

## 🤝 Contributing

1. Follow the **Clean Architecture** principles
2. Write **comprehensive tests** for new features
3. Use **type hints** throughout the codebase
4. Follow **SOLID** principles in design
5. Document **architectural decisions**

## 📚 References

- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)

---

**Architecture Version**: 2.0  
**Last Updated**: 2026-06-25  
**Maintained by**: EndToEndLabCR Team
