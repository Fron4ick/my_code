using System;
using System.Collections.Generic;

class Move
{
    public static void Main()
    {
        var firstArray = new[] { 1, 2, 4, 5 };
        var secondArray = new[] { 1, 3, 4, 6 };
        
        Console.WriteLine("Объединение: " + ArrayToString(UnificationArray(firstArray, secondArray)));
        Console.WriteLine("Пересечение: " + ArrayToString(IntersectionArray(firstArray, secondArray)));
        Console.WriteLine("Разность: " + ArrayToString(DifferenceArray(firstArray, secondArray)));
    }

    public static int[] UnificationArray(int[] firstArray, int[] secondArray)
    {
        // Создаем словарь для подсчета частот
        Dictionary<int, int> frequency = new Dictionary<int, int>();
        
        // Подсчитываем частоты из первого массива
        for (int i = 0; i < firstArray.Length; i++)
        {
            int num = firstArray[i];
            if (frequency.ContainsKey(num))
            {
                frequency[num]++;
            }
            else
            {
                frequency[num] = 1;
            }
        }
        
        // Для второго массива берем максимальное количество вхождений
        for (int i = 0; i < secondArray.Length; i++)
        {
            int num = secondArray[i];
            if (frequency.ContainsKey(num))
            {
                if (frequency[num] < 1)
                {
                    frequency[num] = 1;
                }
            }
            else
            {
                frequency[num] = 1;
            }
        }
        
        // Преобразуем словарь обратно в массив
        List<int> result = new List<int>();
        foreach (var pair in frequency)
        {
            for (int i = 0; i < pair.Value; i++)
            {
                result.Add(pair.Key);
            }
        }
        
        return result.ToArray();
    }

    public static int[] IntersectionArray(int[] firstArray, int[] secondArray)
    {
        // Создаем словари для подсчета частот
        Dictionary<int, int> freq1 = new Dictionary<int, int>();
        Dictionary<int, int> freq2 = new Dictionary<int, int>();
        
        // Подсчитываем частоты для первого массива
        for (int i = 0; i < firstArray.Length; i++)
        {
            int num = firstArray[i];
            if (freq1.ContainsKey(num))
            {
                freq1[num]++;
            }
            else
            {
                freq1[num] = 1;
            }
        }
        
        // Подсчитываем частоты для второго массива
        for (int i = 0; i < secondArray.Length; i++)
        {
            int num = secondArray[i];
            if (freq2.ContainsKey(num))
            {
                freq2[num]++;
            }
            else
            {
                freq2[num] = 1;
            }
        }
        
        // Для пересечения берем минимальное количество вхождений
        List<int> result = new List<int>();
        foreach (var pair in freq1)
        {
            int num = pair.Key;
            if (freq2.ContainsKey(num))
            {
                int minCount = pair.Value < freq2[num] ? pair.Value : freq2[num];
                for (int i = 0; i < minCount; i++)
                {
                    result.Add(num);
                }
            }
        }
        
        return result.ToArray();
    }

    public static int[] DifferenceArray(int[] firstArray, int[] secondArray)
    {
        // Создаем словари для подсчета частот
        Dictionary<int, int> freq1 = new Dictionary<int, int>();
        Dictionary<int, int> freq2 = new Dictionary<int, int>();
        
        // Подсчитываем частоты для первого массива
        for (int i = 0; i < firstArray.Length; i++)
        {
            int num = firstArray[i];
            if (freq1.ContainsKey(num))
            {
                freq1[num]++;
            }
            else
            {
                freq1[num] = 1;
            }
        }
        
        // Подсчитываем частоты для второго массива
        for (int i = 0; i < secondArray.Length; i++)
        {
            int num = secondArray[i];
            if (freq2.ContainsKey(num))
            {
                freq2[num]++;
            }
            else
            {
                freq2[num] = 1;
            }
        }
        
        // Для разности берем разность максимального и минимального количества вхождений
        List<int> result = new List<int>();
        
        // Обрабатываем числа из первого массива
        foreach (var pair in freq1)
        {
            int num = pair.Key;
            int count1 = pair.Value;
            int count2 = freq2.ContainsKey(num) ? freq2[num] : 0;
            
            int diff = count1 - count2;
            if (diff > 0)
            {
                for (int i = 0; i < diff; i++)
                {
                    result.Add(num);
                }
            }
        }
        
        // Обрабатываем числа из второго массива, которых нет в первом
        foreach (var pair in freq2)
        {
            int num = pair.Key;
            if (!freq1.ContainsKey(num))
            {
                for (int i = 0; i < pair.Value; i++)
                {
                    result.Add(num);
                }
            }
        }
        
        return result.ToArray();
    }

    // Вспомогательный метод для красивого вывода массива
    public static string ArrayToString(int[] array)
    {
        if (array == null || array.Length == 0)
            return "[]";
        
        string result = "[";
        for (int i = 0; i < array.Length; i++)
        {
            result += array[i];
            if (i < array.Length - 1)
                result += ", ";
        }
        result += "]";
        return result;
    }
}
