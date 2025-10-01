using System;
using System.ComponentModel.DataAnnotations;
using System.Globalization;

public static class Time
{
    public static void WrongMain()
    {
        // в бинарном виде 0.1 представляется бесконечной дробью 0.00011001100...,
        // в типах данных float и double хранится только начало этой дроби,
        // поэтому число 0.1 представляется с погрешностью. 
        double x = 1.0 / 10; 
        double sum = 0;
        for (int i = 0; i < 10; i++)
            sum += x;
        Console.WriteLine(sum == 1);
    }
    
}
