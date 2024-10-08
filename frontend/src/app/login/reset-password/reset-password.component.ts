import { Component, OnInit } from '@angular/core';
import { NgForm } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import * as _ from 'lodash';
import { AuthService } from '@services/auth.service';
import { HttpErrorResponse } from '@angular/common/http';
import { userIcons } from '@shared/icons';
import { Title } from '@angular/platform-browser';
import { pageTitle } from '@utils/app';

@Component({
    selector: 'ia-reset-password',
    templateUrl: './reset-password.component.html',
    styleUrls: ['./reset-password.component.scss'],
})
export class ResetPasswordComponent implements OnInit {
    public submitted: boolean;
    public resetSucceeded: boolean;
    public passwordRejected: boolean;
    public tokenRejected: boolean;
    public isLoading: boolean;
    public message: string;

    userIcons = userIcons;

    private uid: string;
    private token: string;

    constructor(
        private activatedRoute: ActivatedRoute,
        private authService: AuthService,
        private title: Title,
    ) {}

    ngOnInit() {
        this.activatedRoute.params.subscribe((params) => {
            this.uid = params['uid'];
            this.token = params['token'];
        });
        this.title.setTitle(pageTitle('New password'));
    }

    reset(resetForm: NgForm) {
        this.submitted = true;
        const password = resetForm.value.password;
        this.isLoading = true;
        this.authService
            .resetPassword(this.uid, this.token, password, password)
            .subscribe(
                (res) => {
                    this.handleSuccess(res);
                },
                (errorResponse: HttpErrorResponse) => {
                    this.handleError(errorResponse.error);
                }
            );
    }

    onPasswordChange() {
        if (this.passwordRejected) {
            this.passwordRejected = false;
        }
    }

    private handleSuccess(response: { detail: string }) {
        this.isLoading = false;
        this.resetSucceeded = true;
        this.message = response.detail;
        setTimeout(() => this.authService.showLogin(), 3000);
    }

    private handleError(err) {
        this.isLoading = false;
        if (err.token || err.uid) {
            this.tokenRejected = true;
        } else if (err.new_password1 || err.new_password2) {
            this.passwordRejected = true;
            this.message = _.join(_.values(err));
        } else {
            this.resetSucceeded = false;
            this.message = 'Something unexpected went wrong. Please try again.';
        }
    }
}
