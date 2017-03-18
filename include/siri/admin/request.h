/*
 * request.h - SiriDB Administrative Request.
 *
 * author       : Jeroen van der Heijden
 * email        : jeroen@transceptor.technology
 * copyright    : 2017, Transceptor Technology
 *
 * changes
 *  - initial version, 16-03-2017
 *
 */
#pragma once
#include <qpack/qpack.h>
#include <siri/net/protocol.h>


typedef enum
{
    ADMIN_NEW_ACCOUNT,
    ADMIN_CHANGE_PASSWORD,
    ADMIN_DROP_ACCOUNT,
    ADMIN_NEW_DATABASE
} admin_request_t;

int siri_admin_request_init(void);
void siri_admin_request_destroy(void);
cproto_server_t siri_admin_request(
        int tp,
        qp_unpacker_t * qp_unpacker,
        qp_obj_t * qp_account,
        char * err_msg);
