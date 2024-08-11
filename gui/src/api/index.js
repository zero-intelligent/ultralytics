import request from '@/utils/request'
var baseUrl = location.protocol + '//' + window.location.hostname;
export function getDataHuiji(params) {
  return request({
    url: baseUrl + '/mcd/api.php?a=get_data_huiji',
    method: 'get',
    params: params,
    withCredentials: true
  })
}
export function getDataPeople(params) {
  return request({
    url: baseUrl + '/mcd/api.php?a=get_data_people',
    method: 'get',
    params: params,
    withCredentials: true
  })
}
export function changeTaocan(params) {
  return request({
    url: baseUrl + '/mcd/api.php?a=change_taocan',
    method: 'get',
    params: params,
    withCredentials: true
  })
}
export function getCamraList(params) {
  return request({
    url: baseUrl + '/mcd/api.php?a=get_camra_list',
    method: 'get',
    params: params,
    withCredentials: true
  })
}
export function setCamraList(data) {
  return request({
    url: baseUrl + '/mcd/api.php?a=set_camera',
    method: 'post',
    data,
    withCredentials: true
  })
}
// https://pinda.org.cn/mcd/api.php?a=upload_camera


