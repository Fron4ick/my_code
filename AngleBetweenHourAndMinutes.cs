using System;

public static class Angle
{
    static void Main()
    {
        string[] time = Console.ReadLine().Split(':');
        int hours = int.Parse(time[0]) % 12;
        int minutes = int.Parse(time[1]);
        Console.WriteLine(BetweenHourAndMin(hours, minutes));
    }
    public static double BetweenHourAndMin(int hour, int minutes)
    {
        const int angleHour = 30;
        const int angleMinutes = 6;
        const double angleMinutesInHour = 0.5;

        var angleOurHour = hour * angleHour + angleMinutesInHour * minutes;
        var angleOurMinutes = minutes * angleMinutes;

        var angleBetween = Math.Abs(angleOurMinutes - angleOurHour);
        if (angleBetween > 180)
            return 360 - angleBetween;
        else return angleBetween;
    }
    
}
