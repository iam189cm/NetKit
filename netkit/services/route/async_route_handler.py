"""
异步路由操作处理器
职责：异步操作管理、线程处理、回调管理
"""

import threading
from typing import Callable, Any, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed


class AsyncRouteHandler:
    """异步路由操作处理器 - 负责异步操作和线程管理"""
    
    def __init__(self, max_workers: int = 3):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_tasks = {}
        
    def execute_async(self, operation: Callable, callback: Callable, *args, **kwargs) -> str:
        """异步执行操作"""
        def run_operation():
            try:
                result = operation(*args, **kwargs)
                self._handle_result(result, callback)
            except Exception as e:
                error_result = {
                    'success': False,
                    'error': f"操作执行出错: {str(e)}"
                }
                self._handle_result(error_result, callback)
        
        # 使用线程执行操作
        thread = threading.Thread(target=run_operation, daemon=True)
        task_id = f"task_{id(thread)}"
        self.active_tasks[task_id] = thread
        
        thread.start()
        return task_id
    
    def execute_with_progress(self, operation: Callable, progress_callback: Callable, 
                            result_callback: Callable, *args, **kwargs) -> str:
        """带进度反馈的异步执行"""
        def run_with_progress():
            try:
                # 开始操作
                if progress_callback:
                    progress_callback("操作开始...")
                
                result = operation(*args, **kwargs)
                
                # 操作完成
                if progress_callback:
                    progress_callback("操作完成")
                
                self._handle_result(result, result_callback)
                
            except Exception as e:
                if progress_callback:
                    progress_callback(f"操作失败: {str(e)}")
                
                error_result = {
                    'success': False,
                    'error': f"操作执行出错: {str(e)}"
                }
                self._handle_result(error_result, result_callback)
        
        thread = threading.Thread(target=run_with_progress, daemon=True)
        task_id = f"progress_task_{id(thread)}"
        self.active_tasks[task_id] = thread
        
        thread.start()
        return task_id
    
    def execute_batch_async(self, operations: list, batch_callback: Callable) -> str:
        """批量异步执行操作"""
        def run_batch():
            results = []
            try:
                futures = []
                
                # 提交所有操作到线程池
                for operation, args, kwargs in operations:
                    future = self.executor.submit(operation, *args, **kwargs)
                    futures.append(future)
                
                # 收集结果
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        results.append({
                            'success': False,
                            'error': f"批量操作中的单个操作失败: {str(e)}"
                        })
                
                # 处理批量结果
                batch_result = {
                    'success': True,
                    'results': results,
                    'total': len(operations),
                    'successful': len([r for r in results if r.get('success', False)])
                }
                
                self._handle_result(batch_result, batch_callback)
                
            except Exception as e:
                error_result = {
                    'success': False,
                    'error': f"批量操作执行出错: {str(e)}",
                    'results': results
                }
                self._handle_result(error_result, batch_callback)
        
        thread = threading.Thread(target=run_batch, daemon=True)
        task_id = f"batch_task_{id(thread)}"
        self.active_tasks[task_id] = thread
        
        thread.start()
        return task_id
    
    def _handle_result(self, result: Dict, callback: Callable):
        """处理操作结果"""
        if callback:
            try:
                callback(result)
            except Exception as e:
                print(f"回调函数执行出错: {str(e)}")
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        if task_id in self.active_tasks:
            thread = self.active_tasks[task_id]
            if thread.is_alive():
                # 注意：Python线程无法强制取消，只能等待自然结束
                return False
            else:
                del self.active_tasks[task_id]
                return True
        return False
    
    def get_active_tasks(self) -> list:
        """获取活动任务列表"""
        active = []
        for task_id, thread in list(self.active_tasks.items()):
            if thread.is_alive():
                active.append(task_id)
            else:
                # 清理已完成的任务
                del self.active_tasks[task_id]
        return active
    
    def wait_for_completion(self, timeout: float = None) -> bool:
        """等待所有任务完成"""
        for thread in list(self.active_tasks.values()):
            if thread.is_alive():
                thread.join(timeout=timeout)
                if thread.is_alive():
                    return False
        return True
    
    def cleanup(self):
        """清理资源"""
        # 等待所有任务完成
        self.wait_for_completion(timeout=5.0)
        
        # 关闭线程池
        self.executor.shutdown(wait=True)
        
        # 清理任务列表
        self.active_tasks.clear()
    
    def __del__(self):
        """析构函数"""
        try:
            self.cleanup()
        except:
            pass