import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from PIL import Image
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import json
from datetime import datetime

# --- Конфигурация ---
IMAGE_SIZE = 64  # Размер изображений 64x64
NUM_CLASSES = 10  # Цифры от 0 до 9
BATCH_SIZE = 32
EPOCHS = 50
VALIDATION_SPLIT = 0.2

# Путь к папкам с данными (предполагается структура: data/0/, data/1/, ..., data/9/)
DATA_DIR = "data"  # Измените на путь к вашим папкам

# --- Функции для загрузки данных ---

def load_images_from_folder(folder_path, label):
    """Загружает все изображения из папки и присваивает им метку"""
    images = []
    labels = []
    
    if not os.path.exists(folder_path):
        print(f"Предупреждение: папка {folder_path} не найдена!")
        return images, labels
    
    for filename in os.listdir(folder_path):
        if filename.endswith('.png') or filename.endswith('.jpg'):
            img_path = os.path.join(folder_path, filename)
            try:
                # Загружаем изображение и конвертируем в RGB
                img = Image.open(img_path).convert('RGB')
                
                # Убеждаемся, что размер правильный
                if img.size != (IMAGE_SIZE, IMAGE_SIZE):
                    img = img.resize((IMAGE_SIZE, IMAGE_SIZE))
                
                # Конвертируем в numpy array и нормализуем (0-1)
                img_array = np.array(img, dtype=np.float32) / 255.0
                
                images.append(img_array)
                labels.append(label)
            except Exception as e:
                print(f"Ошибка при загрузке {img_path}: {e}")
    
    return images, labels

def load_dataset(data_dir):
    """Загружает весь датасет из папок 0-9"""
    all_images = []
    all_labels = []
    
    print("Загрузка датасета...")
    for digit in range(NUM_CLASSES):
        folder_path = os.path.join(data_dir, str(digit))
        images, labels = load_images_from_folder(folder_path, digit)
        all_images.extend(images)
        all_labels.extend(labels)
        print(f"Цифра {digit}: загружено {len(images)} изображений")
    
    if len(all_images) == 0:
        raise ValueError("Не загружено ни одного изображения! Проверьте путь к данным.")
    
    print(f"\nВсего загружено: {len(all_images)} изображений")
    
    # Конвертируем в numpy arrays
    X = np.array(all_images)
    y = np.array(all_labels)
    
    # Перемешиваем данные
    indices = np.random.permutation(len(X))
    X = X[indices]
    y = y[indices]
    
    return X, y

# --- Создание модели CNN ---

def create_model(input_shape=(IMAGE_SIZE, IMAGE_SIZE, 3)):
    """Создает сверточную нейронную сеть для классификации цифр"""
    model = keras.Sequential([
        # Первый сверточный блок
        layers.Conv2D(32, (3, 3), activation='relu', padding='same', input_shape=input_shape),
        layers.BatchNormalization(),
        layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Второй сверточный блок
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Третий сверточный блок
        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.4),
        
        # Полносвязные слои
        layers.Flatten(),
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(128, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(NUM_CLASSES, activation='softmax')
    ])
    
    return model

# --- Функции для визуализации ---

def plot_training_history(history, save_path='training_history.png'):
    """Визуализирует процесс обучения"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    # График точности
    ax1.plot(history.history['accuracy'], label='Train Accuracy')
    ax1.plot(history.history['val_accuracy'], label='Val Accuracy')
    ax1.set_title('Model Accuracy')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Accuracy')
    ax1.legend()
    ax1.grid(True)
    
    # График потерь
    ax2.plot(history.history['loss'], label='Train Loss')
    ax2.plot(history.history['val_loss'], label='Val Loss')
    ax2.set_title('Model Loss')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Loss')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig(save_path)
    print(f"График обучения сохранен: {save_path}")
    plt.show()

def plot_predictions(model, X_test, y_test, num_samples=10):
    """Показывает предсказания модели на тестовых данных"""
    indices = np.random.choice(len(X_test), num_samples, replace=False)
    
    fig, axes = plt.subplots(2, 5, figsize=(15, 6))
    axes = axes.ravel()
    
    for i, idx in enumerate(indices):
        img = X_test[idx]
        true_label = y_test[idx]
        
        # Предсказание
        pred = model.predict(np.expand_dims(img, axis=0), verbose=0)
        pred_label = np.argmax(pred)
        confidence = np.max(pred) * 100
        
        # Отображение
        axes[i].imshow(img)
        axes[i].axis('off')
        color = 'green' if pred_label == true_label else 'red'
        axes[i].set_title(f'True: {true_label}, Pred: {pred_label}\n({confidence:.1f}%)', 
                         color=color, fontsize=10)
    
    plt.tight_layout()
    plt.savefig('predictions_sample.png')
    print("Примеры предсказаний сохранены: predictions_sample.png")
    plt.show()

def plot_confusion_matrix(y_true, y_pred):
    """Строит матрицу ошибок"""
    from sklearn.metrics import confusion_matrix
    import seaborn as sns
    
    cm = confusion_matrix(y_true, y_pred)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=range(10), yticklabels=range(10))
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig('confusion_matrix.png')
    print("Матрица ошибок сохранена: confusion_matrix.png")
    plt.show()

# --- Функция предсказания для одного изображения ---

def predict_image(model, image_path):
    """Предсказывает цифру на изображении"""
    try:
        img = Image.open(image_path).convert('RGB')
        img = img.resize((IMAGE_SIZE, IMAGE_SIZE))
        img_array = np.array(img, dtype=np.float32) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        prediction = model.predict(img_array, verbose=0)
        predicted_digit = np.argmax(prediction)
        confidence = np.max(prediction) * 100
        
        print(f"\nПредсказание для {image_path}:")
        print(f"Цифра: {predicted_digit}")
        print(f"Уверенность: {confidence:.2f}%")
        print(f"Все вероятности: {prediction[0]}")
        
        return predicted_digit, confidence
    except Exception as e:
        print(f"Ошибка при предсказании: {e}")
        return None, None

# --- Главная функция ---

def main():
    """Основная функция для обучения модели"""
    
    # Создаем папку для сохранения результатов
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = f"model_results_{timestamp}"
    os.makedirs(results_dir, exist_ok=True)
    
    print("=" * 50)
    print("ОБУЧЕНИЕ НЕЙРОСЕТИ ДЛЯ РАСПОЗНАВАНИЯ ЦИФР")
    print("=" * 50)
    
    # Загрузка данных
    try:
        X, y = load_dataset(DATA_DIR)
    except Exception as e:
        print(f"\nОшибка загрузки данных: {e}")
        print("\nСтруктура папок должна быть следующей:")
        print("data/")
        print("  0/  <- 100 изображений цифры 0")
        print("  1/  <- 100 изображений цифры 1")
        print("  ...")
        print("  9/  <- 100 изображений цифры 9")
        return
    
    # Разделение на train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42, stratify=y
    )
    
    print(f"\nРазмер обучающей выборки: {len(X_train)}")
    print(f"Размер тестовой выборки: {len(X_test)}")
    
    # Создание модели
    print("\nСоздание модели...")
    model = create_model()
    model.summary()
    
    # Компиляция модели
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Callbacks для обучения
    callbacks = [
        keras.callbacks.ModelCheckpoint(
            os.path.join(results_dir, 'best_model.keras'),
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        ),
        keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True,
            verbose=1
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-7,
            verbose=1
        )
    ]
    
    # Обучение
    print("\nНачало обучения...")
    history = model.fit(
        X_train, y_train,
        batch_size=BATCH_SIZE,
        epochs=EPOCHS,
        validation_split=VALIDATION_SPLIT,
        callbacks=callbacks,
        verbose=1
    )
    
    # Оценка на тестовой выборке
    print("\nОценка на тестовой выборке...")
    test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)
    print(f"Тестовая точность: {test_accuracy * 100:.2f}%")
    print(f"Тестовая потеря: {test_loss:.4f}")
    
    # Сохранение финальной модели
    final_model_path = os.path.join(results_dir, 'final_model.keras')
    model.save(final_model_path)
    print(f"\nФинальная модель сохранена: {final_model_path}")
    
    # Сохранение метаданных
    metadata = {
        'image_size': IMAGE_SIZE,
        'num_classes': NUM_CLASSES,
        'total_samples': len(X),
        'train_samples': len(X_train),
        'test_samples': len(X_test),
        'test_accuracy': float(test_accuracy),
        'test_loss': float(test_loss),
        'epochs_trained': len(history.history['loss']),
        'timestamp': timestamp
    }
    
    with open(os.path.join(results_dir, 'metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=4)
    
    # Визуализация
    print("\nСоздание визуализаций...")
    plot_training_history(history, os.path.join(results_dir, 'training_history.png'))
    
    # Предсказания на тестовой выборке
    y_pred = np.argmax(model.predict(X_test, verbose=0), axis=1)
    plot_confusion_matrix(y_test, y_pred)
    plot_predictions(model, X_test, y_test)
    
    print("\n" + "=" * 50)
    print("ОБУЧЕНИЕ ЗАВЕРШЕНО!")
    print(f"Результаты сохранены в папке: {results_dir}")
    print("=" * 50)
    
    return model

# --- Функция для использования обученной модели ---

def load_and_predict(model_path, image_path):
    """Загружает модель и делает предсказание"""
    print(f"Загрузка модели из {model_path}...")
    model = keras.models.load_model(model_path)
    return predict_image(model, image_path)

# --- Запуск ---

if __name__ == "__main__":
    # Обучение модели
    model = main()
    
    # Пример использования обученной модели
    print("\n" + "=" * 50)
    print("ПРИМЕР ИСПОЛЬЗОВАНИЯ МОДЕЛИ")
    print("=" * 50)
    print("\nЧтобы использовать обученную модель для предсказания:")
    print("1. Загрузите модель:")
    print("   model = keras.models.load_model('model_results_XXXXX/best_model.keras')")
    print("2. Сделайте предсказание:")
    print("   predict_image(model, 'path/to/your/image.png')")
    print("\nИли используйте функцию load_and_predict:")
    print("   load_and_predict('model_results_XXXXX/best_model.keras', 'image.png')")
