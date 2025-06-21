#include <stdio.h>
#include <stdlib.h>

int main(int argc, char* argv[]) {
    if (argc != 4) {
        printf("Usage: ./program <num1> <operator> <num2>\n");
        return 1;
    }

    double a = atof(argv[1]);
    char op = argv[2][0];
    double b = atof(argv[3]);
    double result;

    switch (op) {
        case '+': result = a + b; break;
        case '-': result = a - b; break;
        case '*': result = a * b; break;
        case '/':
            if (b == 0) {
                printf("Ошибка: деление на ноль\n");
                return 1;
            }
            result = a / b;
            break;
        default:
            printf("Неизвестная операция: %c\n", op);
            return 1;
    }

    printf("%.2f\n", result);
    return 0;
}