using System;

class Train
{
    public static void Main()
    {
        TestTicket(715068);
        TestTicket(445219);
        TestTicket(012200);
    }

    public static void TestTicket(int ticket)
    {
        Console.WriteLine(IsLuckyTicket(ticket));
    }

    public static string IsLuckyTicket(int ticket)
    {
        var lastTicket = ticket - 1;
        var nextTicket = ticket + 1;
        var luckyLast = (lastTicket / 100000 + lastTicket / 10000 % 10 + lastTicket / 1000 % 100) == (lastTicket / 100 % 1000 + lastTicket / 10 % 10000 + lastTicket % 100000);
        var luckyNext = (luckyNext / 100000 + luckyNext / 10000 % 10 + luckyNext / 1000 % 100) == (luckyNext / 100 % 1000 + luckyNext / 10 % 10000 + luckyNext % 100000);
        return luckyLast || luckyNext;
    }
}
