"""
Utility script to view information about stored embeddings
"""
import chromadb
from pathlib import Path

# Path to embeddings storage
STORAGE_DIR = Path(__file__).parent / "data" / "embeddings_db"

def view_embeddings_info():
    """Display information about stored embeddings"""
    
    if not STORAGE_DIR.exists():
        print("❌ No embeddings storage found!")
        print(f"   Expected location: {STORAGE_DIR}")
        return
    
    try:
        # Connect to persistent storage
        client = chromadb.PersistentClient(path=str(STORAGE_DIR))
        
        # Get collection
        collection = client.get_collection(name="iptv_knowledge")
        
        # Get collection info
        count = collection.count()
        
        print("=" * 60)
        print("📊 EMBEDDINGS STORAGE INFORMATION")
        print("=" * 60)
        print(f"Storage Location: {STORAGE_DIR}")
        print(f"Collection Name:  iptv_knowledge")
        print(f"Total Embeddings: {count}")
        print(f"Storage Format:   ChromaDB Persistent")
        print("=" * 60)
        
        # Calculate storage size
        total_size = 0
        for file in STORAGE_DIR.rglob("*"):
            if file.is_file():
                total_size += file.stat().st_size
        
        size_mb = total_size / (1024 * 1024)
        print(f"Total Storage Size: {size_mb:.2f} MB")
        print("=" * 60)
        
        # List files
        print("\n📁 Storage Files:")
        for file in sorted(STORAGE_DIR.rglob("*")):
            if file.is_file():
                size_kb = file.stat().st_size / 1024
                print(f"   - {file.name} ({size_kb:.1f} KB)")
        
        print("\n" + "=" * 60)
        print("✅ Embeddings are persisted and will load instantly on restart!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error reading embeddings: {e}")

if __name__ == "__main__":
    view_embeddings_info()
