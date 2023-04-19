

function gera_cor(qtd=1){
    var bg_color = []
    var border_color = []
    for(let i = 0; i < qtd; i++){
        let r = Math.random() * 255;
        let g = Math.random() * 255;
        let b = Math.random() * 255;
        bg_color.push(`rgba(${r}, ${g}, ${b}, ${0.2})`)
        border_color.push(`rgba(${r}, ${g}, ${b}, ${1})`)
    }

    return [bg_color, border_color];

}

function renderiza_total_pago(url){
    fetch(url, {
        method: 'get',
    }).then(function(result){
        return result.json()
    }).then(function(data){
        document.getElementById('pago_total').innerHTML = data.total
    })

}

function renderiza_total_solicitado(url){
    fetch(url, {
        method: 'get',
    }).then(function(result){
        return result.json()
    }).then(function(data){
        document.getElementById('solicitado_total').innerHTML = data.total
    })

}

function renderiza_diferenca(url){
    fetch(url, {
        method: 'get',
    }).then(function(result){
        return result.json()
    }).then(function(data){
        document.getElementById('diferenca').innerHTML = data.total
    })

}



function renderiza_pagas(url){
    fetch(url, {
        method: 'get',
    }).then(function(result){
        return result.json()
    }).then(function(data){

        const ctx = document.getElementById('pagas').getContext('2d');
        var cores_faturamento_mensal = gera_cor(qtd=12)
        const myChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],
                datasets: [{
                    label: "Pagas por mês",
                    data: data.data,
                    backgroundColor: cores_faturamento_mensal[0],
                    borderColor: cores_faturamento_mensal[1],
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });


    })
}


function renderiza_solicitadas(url){
    fetch(url, {
        method: 'get',
    }).then(function(result){
        return result.json()
    }).then(function(data){
        const ctx = document.getElementById('solicitadas').getContext('2d');
        var cores_solicitadas = gera_cor(qtd=12)
        const myChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],
                datasets: [{
                    label: "Solicitadas por mês",
                    data: data.data,
                    backgroundColor: cores_solicitadas[0],
                    borderColor: cores_solicitadas[1],
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });


    })
}

//
// function renderiza_produtos_mais_vendidos(url){
//     fetch(url, {
//         method: 'get',
//     }).then(function(result){
//         return result.json()
//     }).then(function(data){
//
//         const ctx = document.getElementById('produtos_mais_vendidos').getContext('2d');
//         var cores_produtos_mais_vendidos = gera_cor(qtd=4)
//         const myChart = new Chart(ctx, {
//             type: 'doughnut',
//             data: {
//                 labels: data.labels,
//                 datasets: [{
//                     label: 'Despesas',
//                     data: data.data,
//                     backgroundColor: cores_produtos_mais_vendidos[0],
//                     borderColor: cores_produtos_mais_vendidos[1],
//                     borderWidth: 1
//                 }]
//             },
//
//         });
//
//
//     })
//
// }
//
// function renderiza_funcionario_mes(url){
//     fetch(url, {
//         method: 'get',
//     }).then(function(result){
//         return result.json()
//     }).then(function(data){
//
//         const ctx = document.getElementById('funcionarios_do_mes').getContext('2d');
//         var cores_funcionarios_do_mes = gera_cor(qtd=4)
//         const myChart = new Chart(ctx, {
//             type: 'polarArea',
//             data: {
//                 labels: data.labels,
//                 datasets: [{
//                     data: data.data,
//                     backgroundColor: cores_funcionarios_do_mes[0],
//                     borderColor: cores_funcionarios_do_mes[1],
//                     borderWidth: 1
//                 }]
//             },
//
//         });
//
//
//     })
//
// }