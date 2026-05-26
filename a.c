#include <stdio.h>

#define ped 3
#define chapa 4


void imprimir_matriz(int l,int matriz[l][l]) {
    for (int i = 0; i < l; i++) {
        for (int j = 0; j < l; j++) {
            if (j%l==0) {
               printf("\t");
            }
            printf("[%3d] ", matriz[i][j]);
        }
        if ((i+1)%l==0) {
               printf("\n");
            }
        printf("\n");
    }
}

int main(int argc, char const *argv[])
{
    int setup[chapa][chapa] = {
        {0, 2, 3, 3},
        {2, 0, 2, 3},
        {1, 4, 0, 3},
        {2,5,1,0}
    };
    int Setup[chapa*chapa][chapa*chapa];

    for (int i = 0; i < chapa; i++)
    {
        for (int j = 0; j < chapa; j++)
        {
            int valor = setup[i][j];
            for (int k = 0; k < chapa; k++)
            {
                for (int l = 0; l < chapa; l++)
                {
                    Setup[i+(chapa*l)][j+(k*chapa)] = valor;
                }
            }
        }  
    }
    
    imprimir_matriz(chapa*chapa, Setup);

    return 0;
}
