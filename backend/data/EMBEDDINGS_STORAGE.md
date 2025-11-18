# Embeddings Storage

## Overview
Embeddings are now saved in **persistent file format** using ChromaDB, allowing for fast loading without regenerating embeddings on every server restart.

## Storage Location
```
backend/data/embeddings_db/
```

## Storage Details
- **Format**: ChromaDB Persistent Storage
- **Database**: SQLite (chroma.sqlite3)
- **Vector Data**: Binary format (data_level0.bin)
- **Total Size**: ~0.59 MB
- **Collection Name**: iptv_knowledge

## Storage Files
- `chroma.sqlite3` (288 KB) - Main database with metadata
- `data_level0.bin` (313.7 KB) - Vector embeddings data
- `header.bin` (0.1 KB) - Header information
- `length.bin` (0.4 KB) - Length metadata
- `link_lists.bin` (0 KB) - HNSW index links

## How It Works

### First Run (Cold Start)
1. System loads article from `backend/data/article.txt`
2. Splits text into chunks (~14 chunks)
3. Generates embeddings using Google Gemini
4. Saves embeddings to persistent storage
5. Console shows: `✅ Saved 14 embeddings to persistent storage`

### Subsequent Runs (Fast Load)
1. System detects existing embeddings in storage
2. Loads embeddings from disk (instant)
3. No API calls needed
4. Console shows: `✅ Loaded existing embeddings from persistent storage`

## Benefits
✅ **No regeneration** - Embeddings persist across restarts
✅ **Instant loading** - No waiting for embedding generation
✅ **Cost savings** - No repeated API calls to Gemini
✅ **Reliability** - Consistent embeddings over time
✅ **Scalability** - Easy to add more documents

## Updating Embeddings
To regenerate embeddings (e.g., after updating article.txt):

1. Delete the embeddings directory:
   ```powershell
   Remove-Item -Recurse -Force backend\data\embeddings_db
   ```

2. Restart the backend server - embeddings will regenerate automatically

## Technical Details
- **Vector Database**: ChromaDB with PersistentClient
- **Embedding Model**: Google Gemini embedding-001
- **Vector Dimensions**: 768 (Gemini standard)
- **Similarity Metric**: Cosine distance
- **Storage Format**: SQLite + Binary files

## Performance
- **Cold start**: ~10-15 seconds (generating embeddings)
- **Warm start**: <1 second (loading from disk)
- **Search time**: ~50-100ms per query
