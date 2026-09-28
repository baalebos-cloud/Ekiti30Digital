"""Application settings loaded from environment variables.

Other leads: add new settings here as needed (e.g. API keys for the
Ask Ekiti / RAG pipeline) rather than reading os.environ directly
elsewhere in the app.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central app configuration.

    Values are read from environment variables (or a local .env file).
    Defaults keep the app runnable out of the box with zero setup.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "EKITI@30 DIGITAL API"

    # SQLite by default so nobody is blocked locally; set DATABASE_URL to a
    # Postgres URL (e.g. postgresql://user:pass@localhost:5432/ekiti30) in
    # .env or docker-compose to use Postgres instead.
    #
    # Note: the Ask Ekiti knowledge base (app/models/knowledge.py) uses a
    # pgvector column for embeddings, which requires Postgres with the
    # pgvector extension (see docker-compose.yml). Running locally against
    # the SQLite default means vector search won't work — that's expected;
    # switch to the Dockerized Postgres to use it.
    DATABASE_URL: str = "sqlite:///./dev.db"

    # Comma-separated list of allowed CORS origins for the frontend, e.g.
    # "http://localhost:3000,https://staging.example.com". Use
    # `cors_origins` (below) to get this parsed into a list.
    FRONTEND_ORIGIN: str = "http://localhost:3000"

    @property
    def cors_origins(self) -> list[str]:
        """FRONTEND_ORIGIN split on commas, with whitespace stripped."""
        return [origin.strip() for origin in self.FRONTEND_ORIGIN.split(",") if origin.strip()]

    # --- Ask Ekiti: LLM / embeddings gateway config (infra only) --------
    #
    # All LLM and embedding calls go through a single gateway ("baalebo")
    # that houses every provider internally behind one endpoint, so the app
    # only needs the gateway's URL and key — never per-provider API keys.
    # All optional and unset by default; no client is implemented yet.
    ASK_EKITI_LLM_WEBHOOK_URL: str | None = None
    ASK_EKITI_LLM_WEBHOOK_KEY: str | None = None

    # Model identifier, expected to be passed in the gateway request
    # payload to select the underlying model/provider. The exact payload
    # shape is unconfirmed until the gateway's API docs arrive — it may
    # also need a separate provider field.
    LLM_MODEL: str | None = None

    # Embeddings are generated locally with sentence-transformers (free,
    # self-hosted) rather than through the gateway. The model is
    # multilingual so Yoruba content embeds meaningfully.
    EMBEDDING_PROVIDER: str = "sentence-transformers"
    EMBEDDING_MODEL: str = "paraphrase-multilingual-MiniLM-L12-v2"

    # Output dimension of EMBEDDING_MODEL (384 for
    # paraphrase-multilingual-MiniLM-L12-v2). Also mirrored as the
    # EMBEDDING_DIMENSIONS constant in app/models/knowledge.py, which the
    # Chunk.embedding column is defined against directly — keep the two in
    # sync by hand; changing it requires a new migration.
    EMBEDDING_DIMENSIONS: int = 384

    # --- Media uploads (Cloudinary) -------------------------------------
    #
    # The browser uploads files directly to Cloudinary using an unsigned
    # preset; these two public, non-secret values are returned to the
    # frontend by POST /api/uploads/init.
    CLOUDINARY_CLOUD_NAME: str | None = None
    CLOUDINARY_UPLOAD_PRESET: str | None = None

    # Secret. Used server-side only, by POST /api/uploads/{id}/complete to
    # look the uploaded resource up via the Cloudinary Admin API (see
    # app/services/cloudinary_admin.py). Never returned to the frontend.
    # Unset means uploads can't be completed (fail closed).
    CLOUDINARY_API_KEY: str | None = None
    CLOUDINARY_API_SECRET: str | None = None

    # --- Admin auth -----------------------------------------------------
    #
    # Shared secret used to verify the JWTs issued by NextAuth in the
    # frontend (see app/core/auth.py). Must equal the frontend's
    # NEXTAUTH_SECRET. Unset means every admin and upload route rejects
    # requests.
    NEXTAUTH_SECRET: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
