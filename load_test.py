

import requests
import time
import threading
import random
import sys
from datetime import datetime
import argparse

class LoadGenerator:
    def __init__(self, base_url, num_threads=10, duration=300):
        
        self.base_url = base_url.rstrip('/')
        self.num_threads = num_threads
        self.duration = duration
        self.stop_flag = False
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'response_times': []
        }
        self.lock = threading.Lock()
        
    def log(self, message, level='INFO'):
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [{level}] {message}")
    
    def make_request(self, method, endpoint, data=None):
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method == 'GET':
                response = requests.get(url, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, timeout=30)
            else:
                raise ValueError(f"Непідтримуваний метод: {method}")
            
            elapsed_time = time.time() - start_time
            
            with self.lock:
                self.stats['total_requests'] += 1
                if response.status_code < 400:
                    self.stats['successful_requests'] += 1
                else:
                    self.stats['failed_requests'] += 1
                self.stats['response_times'].append(elapsed_time)
            
            return response.status_code, elapsed_time
            
        except requests.exceptions.RequestException as e:
            elapsed_time = time.time() - start_time
            with self.lock:
                self.stats['total_requests'] += 1
                self.stats['failed_requests'] += 1
                self.stats['response_times'].append(elapsed_time)
            return None, elapsed_time
    
    def generate_random_user(self):
        random_id = random.randint(1000, 9999)
        return {
            "Name": f"TestUser{random_id}",
            "email": f"test{random_id}@example.com",
            "phone": f"+380{random.randint(100000000, 999999999)}"
        }
    
    def generate_random_category(self):
        categories = ["Electronics", "Furniture", "Clothing", "Books", "Sports"]
        return {
            "CategoryName": f"{random.choice(categories)}{random.randint(100, 999)}",
            "Description": f"Test category description {random.randint(1, 100)}"
        }
    
    def generate_random_property(self):
        return {
            "PropertyName": f"Property{random.randint(100, 999)}",
            "Price": round(random.uniform(10.0, 1000.0), 2),
            "Description": f"Test property description {random.randint(1, 100)}",
            "OwnerID": random.randint(1, 10)
        }
    
    def worker_thread(self, thread_id):
        self.log(f"Потік {thread_id} запущено", "DEBUG")
        
        endpoints = [
            ('GET', '/api/users', None),
            ('GET', '/api/categories', None),
            ('GET', '/api/properties', None),
            ('GET', '/api/property_categories', None),
            ('GET', '/api/docs/', None),  
        ]
        
        post_endpoints = [
            ('POST', '/api/users', lambda: self.generate_random_user()),
            ('POST', '/api/categories', lambda: self.generate_random_category()),
            ('POST', '/api/properties', lambda: self.generate_random_property()),
        ]
        
        request_count = 0
        
        while not self.stop_flag:
         
            if random.random() < 0.8:
                method, endpoint, data = random.choice(endpoints)
            else:
                method, endpoint, data_func = random.choice(post_endpoints)
                data = data_func() if data_func else None
            
            status_code, response_time = self.make_request(method, endpoint, data)
            request_count += 1
            
            if request_count % 10 == 0:
                status_str = f"Status: {status_code}" if status_code else "FAILED"
                self.log(f"Потік {thread_id}: {request_count} запитів, {status_str}, час: {response_time:.3f}s", "DEBUG")
            
            time.sleep(random.uniform(0.1, 0.5))
        
        self.log(f"Потік {thread_id} завершено. Всього запитів: {request_count}", "INFO")
    
    def print_stats(self):
        """Вивід статистики навантаження"""
        with self.lock:
            total = self.stats['total_requests']
            successful = self.stats['successful_requests']
            failed = self.stats['failed_requests']
            response_times = self.stats['response_times']
        
        if total == 0:
            self.log("Немає даних для відображення статистики", "WARNING")
            return
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        success_rate = (successful / total * 100) if total > 0 else 0
        
        print("\n" + "="*60)
        print("СТАТИСТИКА НАВАНТАЖЕННЯ")
        print("="*60)
        print(f"Всього запитів:        {total}")
        print(f"Успішних:              {successful} ({success_rate:.2f}%)")
        print(f"Невдалих:              {failed}")
        print(f"Середній час відповіді: {avg_response_time:.3f} сек")
        print(f"Мінімальний час:       {min_response_time:.3f} сек")
        print(f"Максимальний час:      {max_response_time:.3f} сек")
        print(f"Запитів/сек:           {total / self.duration:.2f}")
        print("="*60 + "\n")
    
    def run(self):
        """Запуск генерування навантаження"""
        self.log(f"Початок тесту навантаження на {self.base_url}", "INFO")
        self.log(f"Параметри: {self.num_threads} потоків, тривалість: {self.duration} сек", "INFO")
        
        
        try:
            response = requests.get(f"{self.base_url}/api/docs/", timeout=10)
            if response.status_code == 200:
                self.log("API доступний, починаємо тест", "INFO")
            else:
                self.log(f"API повернув статус {response.status_code}", "WARNING")
        except Exception as e:
            self.log(f"Не вдалося підключитися до API: {e}", "ERROR")
            self.log("Продовжуємо тест...", "WARNING")
        

        threads = []
        for i in range(self.num_threads):
            thread = threading.Thread(target=self.worker_thread, args=(i,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
     
        start_time = time.time()
        try:
            while time.time() - start_time < self.duration:
                time.sleep(10)  
                elapsed = int(time.time() - start_time)
                remaining = self.duration - elapsed
                with self.lock:
                    total = self.stats['total_requests']
                    successful = self.stats['successful_requests']
                self.log(f"Прогрес: {elapsed}/{self.duration}s | Запитів: {total} | Успішних: {successful} | Залишилось: {remaining}s", "INFO")
        except KeyboardInterrupt:
            self.log("Отримано сигнал переривання, завершуємо тест...", "WARNING")
        
        self.stop_flag = True
        self.log("Очікування завершення потоків...", "INFO")
        for thread in threads:
            thread.join(timeout=5)
        
        self.print_stats()
        
        self.save_results()
    
    def save_results(self):
     
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"load_test_results_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("РЕЗУЛЬТАТИ ТЕСТУ НАВАНТАЖЕННЯ\n")
            f.write("="*60 + "\n")
            f.write(f"URL: {self.base_url}\n")
            f.write(f"Потоків: {self.num_threads}\n")
            f.write(f"Тривалість: {self.duration} сек\n")
            f.write(f"Дата/час: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*60 + "\n\n")
            
            with self.lock:
                total = self.stats['total_requests']
                successful = self.stats['successful_requests']
                failed = self.stats['failed_requests']
                response_times = self.stats['response_times']
            
            if total > 0:
                avg_response_time = sum(response_times) / len(response_times)
                success_rate = (successful / total * 100)
                
                f.write(f"Всього запитів: {total}\n")
                f.write(f"Успішних: {successful} ({success_rate:.2f}%)\n")
                f.write(f"Невдалих: {failed}\n")
                f.write(f"Середній час відповіді: {avg_response_time:.3f} сек\n")
                f.write(f"Мінімальний час: {min(response_times):.3f} сек\n")
                f.write(f"Максимальний час: {max(response_times):.3f} сек\n")
                f.write(f"Запитів/сек: {total / self.duration:.2f}\n")
        
        self.log(f"Результати збережено у файл: {filename}", "INFO")


def main():
    parser = argparse.ArgumentParser(description='Генератор навантаження для REST API')
    parser.add_argument('--url', type=str, default='http://localhost:5000',
                      help='Базовий URL API (за замовчуванням: http://localhost:5000)')
    parser.add_argument('--threads', type=int, default=10,
                      help='Кількість паралельних потоків (за замовчуванням: 10)')
    parser.add_argument('--duration', type=int, default=300,
                      help='Тривалість тесту в секундах (за замовчуванням: 300)')
    
    args = parser.parse_args()
    
    load_gen = LoadGenerator(
        base_url=args.url,
        num_threads=args.threads,
        duration=args.duration
    )
    
    load_gen.run()


if __name__ == '__main__':
    main()

