%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

extern int yylineno;
extern char* yytext;
void yyerror(const char *s);
int yylex();

/* Global Buffer to store the MIPS/Hex text until the end */
char technical_buffer[5000] = "";
char output_buffer[5000] = "";

void print_binary_to_buf(int n, char* buf) {
    for (int i = 31; i >= 0; i--) {
        sprintf(buf + strlen(buf), "%d", (n >> i) & 1);
        if (i % 8 == 0 && i != 0) sprintf(buf + strlen(buf), " ");
    }
}

/* Stores the proof in the buffer instead of printing immediately */
void buffer_technical_proof(const char* id, int val, int offset) {
    char temp[2000];
    // Load immediate
    sprintf(temp, "\n  [Assembly]: DADDIU r1, r0, %d\n", val);
    sprintf(temp + strlen(temp), "  [Binary]:   ");
    // op=011001 (25), rs=00000, rt=00001, imm=val
    int op = 25;
    int rs = 0;
    int rt = 1;
    int imm = val & 0xFFFF;
    char bin[100] = "";
    for(int i=5; i>=0; i--) sprintf(bin + strlen(bin), "%d", (op >> i) & 1);
    sprintf(bin + strlen(bin), " | ");
    for(int i=4; i>=0; i--) sprintf(bin + strlen(bin), "%d", (rs >> i) & 1);
    sprintf(bin + strlen(bin), " | ");
    for(int i=4; i>=0; i--) sprintf(bin + strlen(bin), "%d", (rt >> i) & 1);
    sprintf(bin + strlen(bin), " | ");
    for(int i=15; i>=0; i--) sprintf(bin + strlen(bin), "%d", (imm >> i) & 1);
    sprintf(temp + strlen(temp), "%s\n", bin);
    sprintf(temp + strlen(temp), "              [OP]     [RS]    [RT]    [IMMEDIATE/OFFSET]\n");
    sprintf(temp + strlen(temp), "  [Hex]:      0x%08X\n\n", (op << 26) | (rs << 21) | (rt << 16) | imm);
    // Store
    sprintf(temp + strlen(temp), "  [Assembly]: SD r1, %d(r29) -> %s\n", offset, id);
    sprintf(temp + strlen(temp), "  [Binary]:   ");
    op = 63;
    rs = 29;
    rt = 1;
    imm = offset;
    bin[0] = '\0';
    for(int i=5; i>=0; i--) sprintf(bin + strlen(bin), "%d", (op >> i) & 1);
    sprintf(bin + strlen(bin), " | ");
    for(int i=4; i>=0; i--) sprintf(bin + strlen(bin), "%d", (rs >> i) & 1);
    sprintf(bin + strlen(bin), " | ");
    for(int i=4; i>=0; i--) sprintf(bin + strlen(bin), "%d", (rt >> i) & 1);
    sprintf(bin + strlen(bin), " | ");
    for(int i=15; i>=0; i--) sprintf(bin + strlen(bin), "%d", (imm >> i) & 1);
    sprintf(temp + strlen(temp), "%s\n", bin);
    sprintf(temp + strlen(temp), "              [OP]     [RS]    [RT]    [IMMEDIATE/OFFSET]\n");
    sprintf(temp + strlen(temp), "  [Hex]:      0x%08X\n", (op << 26) | (rs << 21) | (rt << 16) | imm);
    strcat(technical_buffer, temp);
}

/* Symbol Table */
int symbol_table[100]; 
char* variable_names[100];
int offsets[100];
int var_count = 0;

int get_value(char* name) {
    for(int i=0; i<var_count; i++) {
        if(strcmp(variable_names[i], name) == 0) return symbol_table[i];
    }
    return 0;
}

int set_value(char* name, int val) {
    for(int i=0; i<var_count; i++) {
        if(strcmp(variable_names[i], name) == 0) {
            symbol_table[i] = val;
            return offsets[i];
        }
    }
    offsets[var_count] = var_count * 8 + 8;
    variable_names[var_count] = strdup(name);
    symbol_table[var_count++] = val;
    return offsets[var_count-1];
}
%}

%union {
    int num;
    char* id;
    char* str;
}

%token <num> NUMBER
%token <id> ID
%token <str> STRING
%token START END NUM_TYPE ESHOW ASSIGN SEMI COMMA LPAREN RPAREN LBRACE RBRACE
%token PLUS MINUS MULT DIV

%type <num> expr
%left PLUS MINUS
%left MULT DIV

%%
/* We print the [OUTPUT] first, then the buffer, then the success message */
program: START LBRACE stmt_list RBRACE END { 
            char data[1000] = ".data\n";
            for(int i=0; i<var_count; i++) {
                sprintf(data + strlen(data), "           %s  |  Memory Offset: %d\n", variable_names[i], offsets[i]);
            }
            printf("%s%s\n.text\n%s\n=========================================\n          FINAL VARIABLE STATE\n=========================================\n", output_buffer, data, technical_buffer);
            for(int i=0; i<var_count; i++) {
                printf("  Variable: %s        | Value: %d        | Offset: %d\n", variable_names[i], symbol_table[i], offsets[i]);
            }
            printf("=========================================\n\n>>> Execution Successful <<<\n");
         }
       ;

stmt_list: stmt stmt_list | ;

stmt: decl SEMI | assign SEMI | display SEMI | ;

decl: NUM_TYPE ID ASSIGN expr { 
        int off = set_value($2, $4); 
        buffer_technical_proof($2, $4, off); 
    }
    | NUM_TYPE ID { set_value($2, 0); }
    ;

assign: ID ASSIGN expr { 
        int off = set_value($1, $3); 
        buffer_technical_proof($1, $3, off);
    }
    ;

display: ESHOW LPAREN STRING RPAREN { 
            char *s = $3; s[strlen(s)-1] = '\0'; 
            char temp[1000];
            sprintf(temp, "[OUTPUT]: %s\n", s+1);
            strcat(output_buffer, temp);
         }
       | ESHOW LPAREN STRING COMMA ID RPAREN { 
            char *s = $3; s[strlen(s)-1] = '\0'; 
            char temp[1000];
            sprintf(temp, "[OUTPUT]: %s %d\n", s+1, get_value($5));
            strcat(output_buffer, temp);
         }
       ;

expr: expr PLUS expr  { $$ = $1 + $3; }
    | expr MINUS expr { $$ = $1 - $3; }
    | expr MULT expr  { $$ = $1 * $3; }
    | expr DIV expr   { if($3 != 0) $$ = $1 / $3; else { yyerror("Div by zero"); $$ = 0; } }
    | LPAREN expr RPAREN { $$ = $2; }
    | NUMBER          { $$ = $1; }
    | ID              { $$ = get_value($1); }
    ;
%%

void yyerror(const char *s) {
    fprintf(stderr, "Error at line %d: %s near '%s'\n", yylineno, s, yytext);
}

int main() {
    return yyparse();
}