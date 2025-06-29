# SmartUI Frontend Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# 複製 package 文件
COPY package*.json ./
COPY pnpm-lock.yaml ./

# 安裝 pnpm
RUN npm install -g pnpm

# 安裝依賴
RUN pnpm install

# 複製源代碼
COPY . .

# 構建應用
RUN pnpm run build

# 生產階段
FROM nginx:alpine

# 複製構建結果
COPY --from=builder /app/dist /usr/share/nginx/html

# 複製 nginx 配置
COPY nginx.conf /etc/nginx/nginx.conf

# 暴露端口
EXPOSE 80

# 啟動 nginx
CMD ["nginx", "-g", "daemon off;"]

