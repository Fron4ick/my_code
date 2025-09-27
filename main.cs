using System;
using Math;

public static class Angle
{
    static void Main()
    {
        string time = Console.ReadLine().Split();
        int hours = int.Parse(time[0]);
        int minutes = int.Parse(time[1]);
        Console.WriteLine(BetweenHourAndMin(hour, minutes));
    }
    public static double BetweenHourAndMin(int hour, int minutes)
    {
        const var angleHour = 30;
        const var angleMinutes = 6;

        var angleOurHour = hour*angleHour + 0.5*minutes;
        var angleOurMinutes = minutes*angleMinutes;

        var angleBetween = Math.Abs(angleOurMinutes - angleOurHour);
        if (angleBetween > 180)
            return angleBetween - 180;
        else return angleBetween;
    }
    
}
