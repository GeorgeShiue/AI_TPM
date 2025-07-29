import sys
from io import StringIO
from contextlib import contextmanager

@contextmanager
def capture_print_to_file(filename, mode='w'):
    """捕獲指定程式碼塊中的所有 print 輸出到檔案"""
    
    # 保存原始的 stdout
    original_stdout = sys.stdout
    
    # 建立字串緩衝區
    string_buffer = StringIO()
    
    try:
        # 重導向 stdout 到字串緩衝區
        sys.stdout = string_buffer
        yield
    finally:
        # 恢復原始 stdout
        sys.stdout = original_stdout
        
        # 取得捕獲的內容
        captured_output = string_buffer.getvalue()
        
        # 將內容寫入檔案
        with open(filename, mode, encoding='utf-8') as f:
            f.write(captured_output)
        
        # 關閉字串緩衝區
        string_buffer.close()

# 使用範例
with capture_print_to_file('print_output.txt'):
    print("這是第一行輸出")
    print("這是第二行輸出")
    for i in range(3):
        print(f"迴圈第 {i} 次")
    print("程式執行完成")