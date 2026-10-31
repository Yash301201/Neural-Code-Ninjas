FROM node:24-slim AS frontend-build
WORKDIR /frontend-react
COPY frontend-react/package*.json ./
RUN npm ci --no-audit --no-fund
COPY frontend-react/ ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /app/backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ /app/backend/
COPY frontend/ /app/frontend/
COPY --from=frontend-build /frontend-react/dist /app/frontend-react/dist
RUN useradd --create-home appuser
USER appuser
EXPOSE 8000
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
