# 医院智能问答系统 - Android 集成指南

## 📋 目录结构

```
hospital_rag/
├── server.py                 # FastAPI 后端服务
├── rag.py                    # 向量数据库构建脚本
├── query.py                  # 命令行测试工具
├── chroma_db/                # Chroma 向量数据库
├── requirements.txt          # RAG 依赖
└── server_requirements.txt   # 服务端额外依赖
```

---

## 🚀 第一步:启动后端服务

### 1. 安装依赖

```bash
pip install -r server_requirements.txt
```

### 2. 运行服务器

```bash
python server.py
```

服务将在 `http://localhost:8000` 启动,你可以访问:
- **API 文档**: http://localhost:8000/docs (Swagger UI)
- **健康检查**: http://localhost:8000/health
- **根路径**: http://localhost:8000/

### 3. 测试 API

使用浏览器或 curl 测试:

```bash
# 健康检查
curl http://localhost:8000/health

# 发送问题
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"question": "如何挂号?", "top_k": 3}'
```

---

## 📱 第二步:Android 客户端集成

### 方案 A: 使用 Retrofit (推荐)

#### 1. 添加依赖 (`build.gradle`)

```gradle
dependencies {
    // Retrofit for HTTP requests
    implementation 'com.squareup.retrofit2:retrofit:2.9.0'
    implementation 'com.squareup.retrofit2:converter-gson:2.9.0'
    
    // OkHttp logging
    implementation 'com.squareup.okhttp3:logging-interceptor:4.11.0'
}
```

#### 2. 创建数据模型

```kotlin
// data class QueryRequest.kt
data class QueryRequest(
    val question: String,
    val top_k: Int = 3
)

// data class QueryResponse.kt
data class QueryResponse(
    val success: Boolean,
    val answer: String,
    val sources: List<Source>,
    val error: String? = null
)

data class Source(
    val content: String,
    val question: String,
    val answer: String,
    val score: Float
)
```

#### 3. 创建 API 接口

```kotlin
// api/HospitalApiService.kt
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.Call

interface HospitalApiService {
    
    @GET("health")
    fun healthCheck(): Call<Map<String, Any>>
    
    @POST("query")
    fun askQuestion(@Body request: QueryRequest): Call<QueryResponse>
}
```

#### 4. 创建 Retrofit 实例

```kotlin
// api/RetrofitClient.kt
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import java.util.concurrent.TimeUnit

object RetrofitClient {
    
    private const val BASE_URL = "http://YOUR_SERVER_IP:8000/"
    
    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }
    
    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(loggingInterceptor)
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()
    
    val apiService: HospitalApiService by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(HospitalApiService::class.java)
    }
}
```

#### 5. 在 Activity 中调用

```kotlin
// MainActivity.kt
import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    
    private lateinit var etQuestion: EditText
    private lateinit var btnAsk: Button
    private lateinit var tvAnswer: TextView
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        etQuestion = findViewById(R.id.etQuestion)
        btnAsk = findViewById(R.id.btnAsk)
        tvAnswer = findViewById(R.id.tvAnswer)
        
        btnAsk.setOnClickListener {
            val question = etQuestion.text.toString().trim()
            if (question.isNotEmpty()) {
                askQuestion(question)
            } else {
                Toast.makeText(this, "请输入问题", Toast.LENGTH_SHORT).show()
            }
        }
    }
    
    private fun askQuestion(question: String) {
        val request = QueryRequest(question = question, top_k = 3)
        
        RetrofitClient.apiService.askQuestion(request)
            .enqueue(object : retrofit2.Callback<QueryResponse> {
                override fun onResponse(
                    call: Call<QueryResponse>,
                    response: retrofit2.Response<QueryResponse>
                ) {
                    if (response.isSuccessful) {
                        val result = response.body()
                        if (result?.success == true) {
                            tvAnswer.text = result.answer
                        } else {
                            tvAnswer.text = result?.error ?: "未找到答案"
                        }
                    } else {
                        Toast.makeText(this@MainActivity, 
                            "请求失败: ${response.code()}", 
                            Toast.LENGTH_SHORT).show()
                    }
                }
                
                override fun onFailure(call: Call<QueryResponse>, t: Throwable) {
                    Toast.makeText(this@MainActivity, 
                        "网络错误: ${t.message}", 
                        Toast.LENGTH_SHORT).show()
                }
            })
    }
}
```

#### 6. 布局文件 (`activity_main.xml`)

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="16dp">

    <EditText
        android:id="@+id/etQuestion"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="输入您的问题..."
        android:minHeight="100dp"
        android:gravity="top" />

    <Button
        android:id="@+id/btnAsk"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="提问"
        android:layout_marginTop="8dp" />

    <ScrollView
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:layout_marginTop="16dp">

        <TextView
            android:id="@+id/tvAnswer"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:textSize="16sp"
            android:lineSpacingExtra="4dp" />

    </ScrollView>

</LinearLayout>
```

#### 7. 添加网络权限 (`AndroidManifest.xml`)

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

---

### 方案 B: 使用 Volley (更简单)

如果你想要更简单的实现,可以使用 Google Volley:

```kotlin
import com.android.volley.toolbox.JsonObjectRequest
import com.android.volley.toolbox.Volley
import org.json.JSONObject

fun askQuestion(question: String) {
    val queue = Volley.newRequestQueue(this)
    val url = "http://YOUR_SERVER_IP:8000/query"
    
    val jsonBody = JSONObject().apply {
        put("question", question)
        put("top_k", 3)
    }
    
    val request = JsonObjectRequest(
        Request.Method.POST, url, jsonBody,
        { response ->
            val answer = response.getString("answer")
            tvAnswer.text = answer
        },
        { error ->
            Toast.makeText(this, "错误: ${error.message}", Toast.LENGTH_SHORT).show()
        }
    )
    
    queue.add(request)
}
```

---

## 🌐 第三步:部署后端服务

### 选项 1: 本地局域网测试

```bash
# 确保手机和电脑在同一 WiFi
python server.py
```

在 Android 代码中使用电脑的局域网 IP:
```kotlin
private const val BASE_URL = "http://192.168.1.100:8000/"
```

### 选项 2: 云服务器部署 (生产环境)

#### 使用 Docker 部署

创建 `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY server_requirements.txt .
RUN pip install --no-cache-dir -r server_requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "server.py"]
```

构建并运行:

```bash
docker build -t hospital-rag-api .
docker run -p 8000:8000 hospital-rag-api
```

#### 部署到云平台

- **阿里云/腾讯云**: 购买 ECS,安装 Docker,部署服务
- **Heroku**: 免费托管 (需要修改配置)
- **Railway**: 简单易用的云平台

---

## 🔧 常见问题解决

### 1. Android 无法连接服务器

**问题**: `Cleartext HTTP traffic not permitted`

**解决**: 在 `AndroidManifest.xml` 中添加:

```xml
<application
    android:usesCleartextTraffic="true"
    ... >
```

或者使用 HTTPS (推荐生产环境)。

### 2. 响应速度慢

**优化建议**:
- 使用 GPU 加速 Embeddings 模型
- 减少 `top_k` 值
- 使用更快的模型 (如 all-MiniLM-L6-v2 已经是较快的)

### 3. 内存占用高

**优化**:
```python
# 在 server.py 中限制并发
uvicorn.run(app, host="0.0.0.0", port=8000, workers=2)
```

---

## 📊 API 接口说明

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | API 状态 |
| `/health` | GET | 健康检查 |
| `/query` | POST | 问答接口 |
| `/stats` | GET | 数据库统计 |

### POST /query 示例

**请求**:
```json
{
    "question": "初诊患者如何挂号?",
    "top_k": 3
}
```

**响应**:
```json
{
    "success": true,
    "answer": "初诊患者一般需要先进行个人信息登记或建档...",
    "sources": [
        {
            "content": "问题：初诊患者如何在南京市六合区中医院挂号？...",
            "question": "初诊患者如何在南京市六合区中医院挂号？",
            "answer": "初诊患者一般需要先进行个人信息登记或建档...",
            "score": 0.1234
        }
    ]
}
```

---

## 🎯 下一步优化建议

1. **添加用户认证**: JWT Token 验证
2. **缓存机制**: Redis 缓存常见问题
3. **对话历史**: 支持上下文理解
4. **语音输入**: Android 端集成语音识别
5. **离线模式**: 缓存常用问答
6. **推送通知**: 医生排班提醒

---

## 📞 技术支持

如有问题,请检查:
1. 后端服务是否正常运行: `http://YOUR_IP:8000/docs`
2. Android 网络连接是否正常
3. 防火墙是否开放 8000 端口

祝开发顺利! 🚀
