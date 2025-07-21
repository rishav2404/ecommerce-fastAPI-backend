# FastAPI E-commerce Backend Service

A comprehensive FastAPI-based e-commerce backend service with MongoDB integration that handles product management and order processing. Built with production-ready architecture, proper error handling, and extensive documentation.

## 🚀 Features

- **Product Management**: Create and list products with size/quantity inventory
- **Order Processing**: Create orders with automatic inventory validation and updates
- **Advanced Filtering**: Product search by name and size availability
- **Pagination**: Efficient pagination for all list endpoints
- **Data Validation**: Comprehensive input validation using Pydantic
- **Error Handling**: Robust error handling with appropriate HTTP status codes
- **Database Optimization**: MongoDB with proper indexing and connection pooling
- **Production Ready**: Async operations, logging, and configuration management

## 🛠 Technology Stack

- **Framework**: FastAPI 0.104.1
- **Database**: MongoDB with Motor (async driver)
- **Validation**: Pydantic v2
- **Server**: Uvicorn with async support
- **Language**: Python 3.10+

## 📋 API Endpoints

### Products

#### Create Product
```
POST /products
```

**Request Body:**
```json
{
  "name": "Sample Product",
  "price": 100.0,
  "sizes": [
    {
      "size": "M",
      "quantity": 10
    },
    {
      "size": "L", 
      "quantity": 5
    }
  ]
}
```

**Response (201):**
```json
{
  "id": "507f1f77bcf86cd799439011"
}
```

#### List Products
```
GET /products?name=sample&size=M&limit=10&offset=0
```

**Query Parameters:**
- `name` (optional): Filter by product name (partial matching)
- `size` (optional): Filter by available size
- `limit` (optional): Maximum results (1-100, default 10)
- `offset` (optional): Results to skip (default 0)

**Response (200):**
```json
{
  "data": [
    {
      "id": "507f1f77bcf86cd799439011",
      "name": "Sample Product",
      "price": 100.0
    }
  ],
  "page": {
    "next": 10,
    "limit": 10,
    "previous": -10
  }
}
```

### Orders

#### Create Order
```
POST /orders
```

**Request Body:**
```json
{
  "userId": "user_123",
  "items": [
    {
      "productId": "507f1f77bcf86cd799439011",
      "qty": 2
    }
  ]
}
```

**Response (201):**
```json
{
  "id": "507f1f77bcf86cd799439012"
}
```

#### Get User Orders
```
GET /orders/{user_id}?limit=10&offset=0
```

**Response (200):**
```json
{
  "data": [
    {
      "id": "507f1f77bcf86cd799439012",
      "items": [
        {
          "productDetails": {
            "name": "Sample Product",
            "id": "507f1f77bcf86cd799439011"
          },
          "qty": 2
        }
      ],
      "total": 200.0
    }
  ],
  "page": {
    "next": 10,
    "limit": 10,
    "previous": -10
  }
}
```

## 🗄 Database Schema

### Products Collection
```json
{
  "_id": "ObjectId",
  "name": "string",
  "price": "number",
  "sizes": [
    {
      "size": "string",
      "quantity": "number"
    }
  ],
  "created_at": "ISO string",
  "updated_at": "ISO string"
}
```

### Orders Collection
```json
{
  "_id": "ObjectId", 
  "userId": "string",
  "items": [
    {
      "productId": "string",
      "qty": "number"
    }
  ],
  "total": "number",
  "created_at": "ISO string",
  "updated_at": "ISO string"
}
```

**Database Indexes:**
- Products: `name`, `sizes.size`
- Orders: `userId`, `createdAt`

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- MongoDB instance (local or Atlas)
- pip package manager

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd ecommerce-backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment Configuration**
```bash
cp .env.example .env
```

Edit `.env` file with your configuration:
```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=ecommerce
MONGODB_ATLAS_URL=mongodb+srv://username:password@cluster0.mongodb.net/
DEBUG=True
```

### Database Setup

#### Option 1: MongoDB Atlas (Recommended)
1. Create a free account at [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a new M0 (free) cluster
3. Get your connection string
4. Update `MONGODB_ATLAS_URL` in `.env`

#### Option 2: Local MongoDB
1. Install MongoDB locally
2. Start MongoDB service
3. Update `MONGODB_URL` in `.env` if needed

### Running the Application

#### Development Mode
```bash
python -m app.main
```

or

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testing

### Manual Testing
Use the interactive API documentation at `/docs` to test all endpoints.

### Health Check
```bash
curl http://localhost:8000/health
```

### Sample API Calls

#### Create a Product
```bash
curl -X POST "http://localhost:8000/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "T-Shirt",
    "price": 29.99,
    "sizes": [
      {"size": "S", "quantity": 10},
      {"size": "M", "quantity": 15},
      {"size": "L", "quantity": 8}
    ]
  }'
```

#### List Products
```bash
curl "http://localhost:8000/products?name=shirt&limit=5"
```

#### Create an Order
```bash
curl -X POST "http://localhost:8000/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user_123",
    "items": [
      {"productId": "PRODUCT_ID_HERE", "qty": 2}
    ]
  }'
```

#### Get User Orders
```bash
curl "http://localhost:8000/orders/user_123"
```

## 📁 Project Structure

```
app/
├── __init__.py
├── main.py                 # FastAPI application setup
├── config.py              # Configuration management
├── models/                # Pydantic models
│   ├── __init__.py
│   ├── product.py         # Product data models
│   └── order.py           # Order data models
├── services/              # Business logic layer
│   ├── __init__.py
│   ├── product_service.py # Product operations
│   └── order_service.py   # Order operations
├── routes/                # API route handlers
│   ├── __init__.py
│   ├── products.py        # Product endpoints
│   └── orders.py          # Order endpoints
└── database/              # Database connection
    ├── __init__.py
    └── connection.py      # MongoDB connection
```

## 🔧 Configuration

Environment variables in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URL` | Local MongoDB URL | `mongodb://localhost:27017` |
| `DATABASE_NAME` | Database name | `ecommerce` |
| `MONGODB_ATLAS_URL` | Atlas connection string | None |
| `DEBUG` | Enable debug mode | `False` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |

## 🔒 Business Logic

### Product Management
- Products must have at least one size
- Size names cannot be duplicated within a product
- All prices must be positive
- Inventory is tracked per size

### Order Processing
- Orders validate product availability before creation
- Inventory is automatically updated when orders are created
- Order totals are calculated based on current product prices
- Orders cannot be created for out-of-stock products

### Data Validation
- All input data is validated using Pydantic models
- Proper error messages are returned for validation failures
- Database operations include error handling

## 🚨 Error Handling

The API returns appropriate HTTP status codes:

- `200`: Successful GET requests
- `201`: Successful resource creation
- `400`: Bad request (validation errors, insufficient inventory)
- `404`: Resource not found
- `500`: Internal server error

## 🔍 Monitoring & Logging

- Comprehensive logging throughout the application
- Health check endpoints for monitoring
- Request/response logging in debug mode
- Database connection status monitoring

## 🔮 Production Considerations

For production deployment:

1. **Security**: Implement authentication and authorization
2. **Transactions**: Use MongoDB transactions for order processing
3. **Caching**: Add Redis for frequently accessed data
4. **Rate Limiting**: Implement API rate limiting
5. **Monitoring**: Add application monitoring (e.g., Prometheus)
6. **Testing**: Add comprehensive test suite
7. **CI/CD**: Implement continuous integration/deployment
8. **Environment**: Use proper environment separation

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For questions or issues:
- Check the API documentation at `/docs`
- Review the logs for error details
- Ensure MongoDB connection is working
- Verify environment configuration